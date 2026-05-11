"""
Rice Leaf Disease — Model Training Script

Two-phase training strategy on EfficientNet-B3:
  Phase 1: Train only the classifier head (10 epochs, lr=1e-3)
  Phase 2: Fine-tune last 2 blocks + head (20 epochs, lr=1e-4)

Usage:
    python -m ml.train --data_dir ./data/rice_disease --epochs1 10 --epochs2 20

Dataset structure expected:
    data/rice_disease/
    ├── Healthy/
    ├── Blast/
    ├── BrownSpot/
    ├── SheathBlight/
    ├── BacterialLeafBlight/
    ├── Tungro/
    ├── FalseSmut/
    └── NarrowBrownLeafSpot/
"""

import os
import json
import argparse
import logging
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
from sklearn.metrics import f1_score, classification_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ─── Disease class mapping ───
CLASS_NAMES = [
    "Healthy",
    "Blast",
    "BrownSpot",
    "SheathBlight",
    "BacterialLeafBlight",
    "Tungro",
    "FalseSmut",
    "NarrowBrownLeafSpot",
]
NUM_CLASSES = len(CLASS_NAMES)


def get_transforms():
    """Training and validation transforms."""
    train_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(30),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1, hue=0.05),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    return train_transform, val_transform


def build_model(num_classes: int) -> nn.Module:
    """Build EfficientNet-B3 with custom classifier head."""
    model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.IMAGENET1K_V1)

    # Freeze all parameters initially
    for param in model.parameters():
        param.requires_grad = False

    # Replace classifier head
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(1536, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.3),
        nn.Linear(512, num_classes),
    )

    return model


def unfreeze_last_n_blocks(model: nn.Module, n: int = 2):
    """Unfreeze the last n feature blocks for fine-tuning."""
    # EfficientNet features are indexed 0-8
    total_blocks = len(model.features)
    for i in range(total_blocks - n, total_blocks):
        for param in model.features[i].parameters():
            param.requires_grad = True
    logger.info(f"Unfroze last {n} feature blocks ({total_blocks - n} to {total_blocks - 1})")


def compute_class_weights(dataset) -> torch.Tensor:
    """Compute inverse-frequency class weights for imbalanced datasets."""
    targets = []
    for _, label in dataset:
        targets.append(label)
    targets = np.array(targets)

    class_counts = np.bincount(targets, minlength=NUM_CLASSES)
    total = len(targets)
    weights = total / (NUM_CLASSES * class_counts.astype(float) + 1e-6)
    weights = weights / weights.sum() * NUM_CLASSES  # normalize

    logger.info(f"Class distribution: {dict(zip(CLASS_NAMES, class_counts.tolist()))}")
    logger.info(f"Class weights: {dict(zip(CLASS_NAMES, np.round(weights, 3).tolist()))}")

    return torch.FloatTensor(weights)


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch. Returns average loss, accuracy, and F1."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []

    for batch_idx, (images, labels) in enumerate(dataloader):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

        all_preds.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    avg_loss = running_loss / total
    accuracy = correct / total
    f1 = f1_score(all_labels, all_preds, average="weighted")

    return avg_loss, accuracy, f1


def evaluate(model, dataloader, criterion, device):
    """Evaluate on validation set. Returns loss, accuracy, F1, preds, labels."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    avg_loss = running_loss / total
    accuracy = correct / total
    f1 = f1_score(all_labels, all_preds, average="weighted")

    return avg_loss, accuracy, f1, all_preds, all_labels


def main():
    parser = argparse.ArgumentParser(description="Train EfficientNet-B3 for Rice Disease Classification")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to dataset root")
    parser.add_argument("--output_dir", type=str, default="./ml/model", help="Where to save checkpoints")
    parser.add_argument("--epochs1", type=int, default=10, help="Phase 1 epochs (classifier only)")
    parser.add_argument("--epochs2", type=int, default=20, help="Phase 2 epochs (fine-tune)")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr1", type=float, default=1e-3, help="Phase 1 learning rate")
    parser.add_argument("--lr2", type=float, default=1e-4, help="Phase 2 learning rate")
    parser.add_argument("--num_workers", type=int, default=4, help="DataLoader workers")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    os.makedirs(args.output_dir, exist_ok=True)

    # ─── Load Dataset ───
    train_transform, val_transform = get_transforms()

    full_dataset = datasets.ImageFolder(args.data_dir, transform=train_transform)
    logger.info(f"Found {len(full_dataset)} images in {len(full_dataset.classes)} classes")
    logger.info(f"Classes: {full_dataset.classes}")

    # ─── Split: 70% train, 15% val, 15% test ───
    total = len(full_dataset)
    train_size = int(0.70 * total)
    val_size = int(0.15 * total)
    test_size = total - train_size - val_size

    train_dataset, val_dataset, test_dataset = random_split(
        full_dataset, [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42)
    )

    logger.info(f"Split — Train: {train_size}, Val: {val_size}, Test: {test_size}")

    # Override transforms for val/test
    val_dataset.dataset.transform = val_transform

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers, pin_memory=True)

    # ─── Model ───
    model = build_model(NUM_CLASSES).to(device)

    # ─── Class weights ───
    class_weights = compute_class_weights(train_dataset).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # ─── Training Log ───
    training_log = []
    best_val_acc = 0.0

    # ════════════════════════════════════════════════
    # PHASE 1: Train classifier head only
    # ════════════════════════════════════════════════
    logger.info("=" * 60)
    logger.info("PHASE 1: Training classifier head (backbone frozen)")
    logger.info("=" * 60)

    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr1, weight_decay=1e-4
    )

    for epoch in range(1, args.epochs1 + 1):
        train_loss, train_acc, train_f1 = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, val_f1, _, _ = evaluate(model, val_loader, criterion, device)

        log_entry = {
            "phase": 1, "epoch": epoch,
            "train_loss": round(train_loss, 4), "train_acc": round(train_acc, 4), "train_f1": round(train_f1, 4),
            "val_loss": round(val_loss, 4), "val_acc": round(val_acc, 4), "val_f1": round(val_f1, 4),
        }
        training_log.append(log_entry)

        logger.info(
            f"[P1 Epoch {epoch}/{args.epochs1}] "
            f"Train: loss={train_loss:.4f} acc={train_acc:.4f} f1={train_f1:.4f} | "
            f"Val: loss={val_loss:.4f} acc={val_acc:.4f} f1={val_f1:.4f}"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            save_checkpoint(model, optimizer, epoch, val_acc, args.output_dir, "best")
            logger.info(f"  ✅ New best model saved (val_acc={val_acc:.4f})")

    # ════════════════════════════════════════════════
    # PHASE 2: Fine-tune last 2 blocks + classifier
    # ════════════════════════════════════════════════
    logger.info("=" * 60)
    logger.info("PHASE 2: Fine-tuning last 2 blocks + classifier")
    logger.info("=" * 60)

    unfreeze_last_n_blocks(model, n=2)

    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr2, weight_decay=1e-4
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs2, eta_min=1e-6)

    for epoch in range(1, args.epochs2 + 1):
        train_loss, train_acc, train_f1 = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, val_f1, _, _ = evaluate(model, val_loader, criterion, device)
        scheduler.step()

        log_entry = {
            "phase": 2, "epoch": epoch,
            "train_loss": round(train_loss, 4), "train_acc": round(train_acc, 4), "train_f1": round(train_f1, 4),
            "val_loss": round(val_loss, 4), "val_acc": round(val_acc, 4), "val_f1": round(val_f1, 4),
            "lr": round(optimizer.param_groups[0]["lr"], 6),
        }
        training_log.append(log_entry)

        logger.info(
            f"[P2 Epoch {epoch}/{args.epochs2}] "
            f"Train: loss={train_loss:.4f} acc={train_acc:.4f} f1={train_f1:.4f} | "
            f"Val: loss={val_loss:.4f} acc={val_acc:.4f} f1={val_f1:.4f} | "
            f"LR: {optimizer.param_groups[0]['lr']:.6f}"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            save_checkpoint(model, optimizer, epoch, val_acc, args.output_dir, "best")
            logger.info(f"  ✅ New best model saved (val_acc={val_acc:.4f})")

    # ─── Final Evaluation on Test Set ───
    logger.info("=" * 60)
    logger.info("FINAL EVALUATION ON TEST SET")
    logger.info("=" * 60)

    # Load best model
    best_path = os.path.join(args.output_dir, "efficientnet_rice.pth")
    checkpoint = torch.load(best_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])

    test_loss, test_acc, test_f1, test_preds, test_labels = evaluate(model, test_loader, criterion, device)
    logger.info(f"Test — Loss: {test_loss:.4f}, Accuracy: {test_acc:.4f}, F1: {test_f1:.4f}")
    logger.info(f"\n{classification_report(test_labels, test_preds, target_names=CLASS_NAMES)}")

    # ─── Save Training Log ───
    log_path = os.path.join(args.output_dir, "training_log.json")
    with open(log_path, "w") as f:
        json.dump({
            "best_val_accuracy": round(best_val_acc, 4),
            "test_accuracy": round(test_acc, 4),
            "test_f1": round(test_f1, 4),
            "num_classes": NUM_CLASSES,
            "class_names": CLASS_NAMES,
            "timestamp": datetime.now().isoformat(),
            "epochs": training_log,
        }, f, indent=2)
    logger.info(f"Training log saved to {log_path}")
    logger.info(f"🎉 Training complete! Best val accuracy: {best_val_acc:.4f}")


def save_checkpoint(model, optimizer, epoch, val_acc, output_dir, tag="best"):
    """Save model checkpoint."""
    path = os.path.join(output_dir, "efficientnet_rice.pth")
    torch.save({
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "epoch": epoch,
        "val_accuracy": val_acc,
    }, path)


if __name__ == "__main__":
    main()
