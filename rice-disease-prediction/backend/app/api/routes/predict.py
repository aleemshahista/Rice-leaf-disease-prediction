"""
Prediction route — upload an image and get disease classification.
"""

import io
import logging

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from PIL import Image

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.prediction import Prediction
from app.services.ml_service import ml_service
from app.services.gradcam_service import generate_gradcam, gradcam_to_bytes
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Prediction"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MIN_DIMENSION = 100


@router.post("/predict")
def predict_disease(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a rice leaf image and get disease prediction.

    Accepts: JPEG or PNG, max 10MB, minimum 100x100 pixels.
    Returns prediction with confidence, Grad-CAM heatmap, and treatment info.
    """

    # ─── Validate file type ───
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file.content_type}'. Only JPEG and PNG are accepted.",
        )

    # ─── Read and validate size ───
    file_bytes = file.file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({len(file_bytes) / 1024 / 1024:.1f}MB). Maximum is 10MB.",
        )

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded.",
        )

    # ─── Open and validate dimensions ───
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()
        # Re-open after verify (verify closes the file)
        image = Image.open(io.BytesIO(file_bytes))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or corrupted image file.",
        )

    width, height = image.size
    if width < MIN_DIMENSION or height < MIN_DIMENSION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image too small ({width}x{height}). Minimum is {MIN_DIMENSION}x{MIN_DIMENSION} pixels.",
        )

    # ─── Upload original image to storage ───
    image_url = storage_service.upload_image(
        file_bytes, file.filename or "upload.jpg", folder="images"
    )

    # ─── Run ML inference ───
    try:
        predicted_class, confidence, all_probs = ml_service.predict(image)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction failed. Please try again.",
        )

    # ─── Get disease info ───
    disease_info = ml_service.get_disease_info(predicted_class)

    # ─── Generate Grad-CAM heatmap ───
    gradcam_url = None
    try:
        gradcam_image = generate_gradcam(image, target_class=predicted_class)
        if gradcam_image:
            gradcam_bytes = gradcam_to_bytes(gradcam_image)
            gradcam_url = storage_service.upload_image(
                gradcam_bytes, "gradcam.png", folder="gradcam"
            )
    except Exception as e:
        logger.warning(f"Grad-CAM generation failed (non-critical): {e}")

    # ─── Save prediction to database ───
    prediction = Prediction(
        user_id=current_user.id,
        image_url=image_url,
        disease_class=predicted_class,
        disease_name=disease_info["name"],
        confidence=confidence,
        all_probs=all_probs,
        gradcam_url=gradcam_url,
        treatment=disease_info["treatment"],
        severity=disease_info["severity"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    # ─── Build response ───
    return {
        "status": "success",
        "data": {
            "prediction_id": prediction.id,
            "disease_name": disease_info["name"],
            "description": disease_info["description"],
            "symptoms": disease_info["symptoms"],
            "confidence": round(confidence, 4),
            "all_probabilities": all_probs,
            "gradcam_url": gradcam_url,
            "image_url": image_url,
            "treatment": disease_info["treatment"],
            "severity": disease_info["severity"],
            "timestamp": prediction.created_at.isoformat(),
        },
        "message": (
            "Prediction completed successfully"
            + (" (demo mode)" if ml_service.demo_mode else "")
        ),
    }
