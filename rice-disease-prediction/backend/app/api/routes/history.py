"""
Prediction history routes — view and manage past predictions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.prediction import Prediction
from app.services.storage_service import storage_service

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("")
def get_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    disease: Optional[str] = Query(None, description="Filter by disease name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paginated prediction history for the current user."""

    query = db.query(Prediction).filter(Prediction.user_id == current_user.id)

    # Apply disease filter
    if disease:
        query = query.filter(Prediction.disease_name.ilike(f"%{disease}%"))

    # Total count
    total = query.count()

    # Paginate
    predictions = (
        query.order_by(Prediction.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    data = [
        {
            "prediction_id": p.id,
            "disease_name": p.disease_name,
            "confidence": p.confidence,
            "severity": p.severity,
            "image_url": p.image_url,
            "gradcam_url": p.gradcam_url,
            "timestamp": p.created_at.isoformat(),
        }
        for p in predictions
    ]

    return {
        "status": "success",
        "data": data,
        "total": total,
        "page": page,
        "per_page": per_page,
        "message": "History retrieved successfully",
    }


@router.get("/{prediction_id}")
def get_prediction_detail(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get full details for a single prediction."""

    prediction = (
        db.query(Prediction)
        .filter(
            Prediction.id == prediction_id,
            Prediction.user_id == current_user.id,
        )
        .first()
    )

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )

    return {
        "status": "success",
        "data": {
            "prediction_id": prediction.id,
            "disease_name": prediction.disease_name,
            "confidence": prediction.confidence,
            "all_probabilities": prediction.all_probs,
            "gradcam_url": prediction.gradcam_url,
            "image_url": prediction.image_url,
            "treatment": prediction.treatment,
            "severity": prediction.severity,
            "timestamp": prediction.created_at.isoformat(),
        },
        "message": "Prediction details retrieved",
    }


@router.delete("/{prediction_id}")
def delete_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a prediction record."""

    prediction = (
        db.query(Prediction)
        .filter(
            Prediction.id == prediction_id,
            Prediction.user_id == current_user.id,
        )
        .first()
    )

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )

    # Delete stored images
    if prediction.image_url:
        storage_service.delete_image(prediction.image_url)
    if prediction.gradcam_url:
        storage_service.delete_image(prediction.gradcam_url)

    db.delete(prediction)
    db.commit()

    return {
        "status": "success",
        "data": None,
        "message": "Prediction deleted successfully",
    }
