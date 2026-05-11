"""
Standalone inference script — test single images from CLI.

Usage:
    python -m ml.inference --image_path ./test_leaf.jpg --model_path ./ml/model/efficientnet_rice.pth
"""

import argparse
import logging

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

CLASS_NAMES = [
    "Healthy", "Blast", "BrownSpot", "SheathBlight",
    "BacterialLeafBlight", "Tungro", "FalseSmut", "NarrowBrownLeafSpot",
]


def main():
    parser = argparse.ArgumentParser(description="Single image inference")
    parser.add_argument("--image_path", type=str, required=True)
    parser.add_argument("--model_path", type=str, default="./ml/model/efficientnet_rice.pth")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Build model
    model = models.efficientnet_b3(weights=None)
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(1536, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.3),
        nn.Linear(512, len(CLASS_NAMES)),
    )

    # Load weights
    checkpoint = torch.load(args.model_path, map_location=device, weights_only=False)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)

    model.to(device)
    model.eval()

    # Preprocess image
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    image = Image.open(args.image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(device)

    # Inference
    with torch.no_grad():
        outputs = model(input_tensor)
        probs = F.softmax(outputs, dim=1)[0]

    # Results
    logger.info(f"\n{'='*50}")
    logger.info(f"Image: {args.image_path}")
    logger.info(f"{'='*50}")

    sorted_indices = probs.argsort(descending=True)
    for i, idx in enumerate(sorted_indices):
        idx = idx.item()
        name = CLASS_NAMES[idx]
        prob = probs[idx].item()
        marker = " ◀ PREDICTED" if i == 0 else ""
        logger.info(f"  {name:.<30} {prob:>6.2%}{marker}")

    logger.info(f"{'='*50}")


if __name__ == "__main__":
    main()
