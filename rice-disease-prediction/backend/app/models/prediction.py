"""
Prediction ORM model.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    disease_class: Mapped[int] = mapped_column(Integer, nullable=False)
    disease_name: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    all_probs: Mapped[dict] = mapped_column(JSON, nullable=True)
    gradcam_url: Mapped[str] = mapped_column(String(500), nullable=True)
    treatment: Mapped[dict] = mapped_column(JSON, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="predictions")

    def __repr__(self) -> str:
        return f"<Prediction {self.disease_name} ({self.confidence:.1%})>"
