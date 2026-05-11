"""
Model evaluation script — run on test set and generate metrics.

Usage:
    python -m ml.evaluate --data_dir ./data/rice_disease --model_path ./ml/model/efficientnet_rice.pth
"""

import os
import json
import argparse
import logging

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
from sklearn.metrics import (
    classification_report, confusion_matrix, f1_score, accuracy_score
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

CLASS_NAMES = [
    "Healthy", "Blast", "BrownSpot", "SheathBlight",
    "BacterialLeafBlight", "Tungro", "FalseSmut", "NarrowBrownLeafSpot",
]
NUM_CLASSES = len(CLASS_NAMES)


def build_model(num_classes: int) -> nn.Module:
    """Build EfficientNet-B3 with custom classifier."""
    model = models.efficientnet_b3(weights=None)
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(1536, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.3),
        nn.Linear(512, num_classes),
    )
    return model


def main():
    parser = argparse.ArgumentParser(description="Evaluate trained model")
    parser.add_argument("--data_dir", type=str, required=True)
    parser.add_argument("--model_path", type=str, default="./ml/model/efficientnet_rice.pth")
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--output_dir", type=str, default="./ml/model")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # ─── Transform ───
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # ─── Dataset ───
    full_dataset = datasets.ImageFolder(args.data_dir, transform=transform)
    total = len(full_dataset)
    train_size = int(0.70 * total)
    val_size = int(0.15 * total)
    test_size = total - train_size - val_size

    _, _, test_dataset = random_split(
        full_dataset, [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42)
    )

    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=4)
    logger.info(f"Test set size: {len(test_dataset)}")

    # ─── Load Model ───
    model = build_model(NUM_CLASSES).to(device)
    checkpoint = torch.load(args.model_path, map_location=device, weights_only=False)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)
    model.eval()
    logger.info("Model loaded successfully")

    # ─── Evaluate ───
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            _, predicted = outputs.max(1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    # ─── Metrics ───
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average="weighted")
    cm = confusion_matrix(all_labels, all_preds)
    report = classification_report(all_labels, all_preds, target_names=CLASS_NAMES)

    logger.info(f"\n{'='*60}")
    logger.info(f"Test Accuracy: {accuracy:.4f}")
    logger.info(f"Test F1 Score: {f1:.4f}")
    logger.info(f"\nClassification Report:\n{report}")
    logger.info(f"\nConfusion Matrix:\n{cm}")

    # ─── Save Results ───
    results = {
        "accuracy": round(accuracy, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm.tolist(),
        "classification_report": classification_report(
            all_labels, all_preds, target_names=CLASS_NAMES, output_dict=True
        ),
    }

    output_path = os.path.join(args.output_dir, "evaluation_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
