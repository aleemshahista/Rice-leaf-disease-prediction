"""
Grad-CAM visualization service.

Generates heatmap overlays showing which regions of the leaf
the model focused on when making its prediction.
"""

import io
import logging
from typing import Optional

import numpy as np
from PIL import Image

import torch

from app.services.ml_service import ml_service

logger = logging.getLogger(__name__)


def generate_gradcam(image: Image.Image, target_class: Optional[int] = None) -> Optional[Image.Image]:
    """
    Generate a Grad-CAM heatmap overlay for the given image.

    Args:
        image: Original PIL Image
        target_class: Target class index (uses predicted class if None)

    Returns:
        PIL Image with heatmap overlay, or None if generation fails
    """
    try:
        # Import here to handle missing dependency gracefully
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.image import show_cam_on_image
        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

        model = ml_service.model

        if model is None:
            logger.warning("No model loaded — skipping Grad-CAM generation")
            return None

        # Get the target layer (last conv layer of EfficientNet-B3)
        # EfficientNet features[-1] is the last block
        target_layers = [model.features[-1]]

        # Preprocess image
        input_tensor = ml_service.get_input_tensor(image)

        # Prepare the original image as a numpy array (0-1 range)
        rgb_img = image.convert("RGB").resize((224, 224))
        rgb_np = np.array(rgb_img).astype(np.float32) / 255.0

        # Create Grad-CAM
        cam = GradCAM(model=model, target_layers=target_layers)

        targets = None
        if target_class is not None:
            targets = [ClassifierOutputTarget(target_class)]

        # Generate the CAM
        grayscale_cam = cam(input_tensor=input_tensor, targets=targets)
        grayscale_cam = grayscale_cam[0, :]  # Take first (and only) image in batch

        # Create overlay
        visualization = show_cam_on_image(rgb_np, grayscale_cam, use_rgb=True)
        result_image = Image.fromarray(visualization)

        logger.info(f"Grad-CAM generated successfully for class {target_class}")
        return result_image

    except ImportError:
        logger.warning("pytorch-grad-cam not installed — skipping Grad-CAM")
        return None
    except Exception as e:
        logger.error(f"Grad-CAM generation failed: {e}")
        return None


def gradcam_to_bytes(gradcam_image: Image.Image) -> bytes:
    """Convert a Grad-CAM PIL Image to PNG bytes."""
    buffer = io.BytesIO()
    gradcam_image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.read()
