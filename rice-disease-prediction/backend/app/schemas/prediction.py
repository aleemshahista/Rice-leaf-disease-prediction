"""
Pydantic schemas for Prediction endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProbabilityItem(BaseModel):
    """Single class probability."""
    class_name: str
    probability: float


class PredictionResponse(BaseModel):
    """Full prediction result."""
    status: str = "success"
    data: "PredictionData"
    message: str = "Prediction completed successfully"


class PredictionData(BaseModel):
    """Prediction data payload."""
    prediction_id: str
    disease_name: str
    confidence: float
    all_probabilities: List[ProbabilityItem]
    gradcam_url: Optional[str] = None
    image_url: str
    treatment: Dict[str, Any]
    severity: str
    timestamp: datetime

    class Config:
        from_attributes = True


class PredictionListItem(BaseModel):
    """Abbreviated prediction for list views."""
    prediction_id: str
    disease_name: str
    confidence: float
    severity: str
    image_url: str
    gradcam_url: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class PredictionListResponse(BaseModel):
    """Paginated prediction history."""
    status: str = "success"
    data: List[PredictionListItem]
    total: int
    page: int
    per_page: int
    message: str = "History retrieved successfully"


class PredictionDetailResponse(BaseModel):
    """Single prediction detail view."""
    status: str = "success"
    data: PredictionData
    message: str = "Prediction details retrieved"
