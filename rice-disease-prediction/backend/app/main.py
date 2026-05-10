"""
Rice Disease Prediction API — FastAPI Application Entrypoint

This module creates and configures the FastAPI application with:
- CORS middleware for frontend communication
- Rate limiting on prediction endpoints
- Static file serving for uploaded images
- Auto-generated API docs at /docs
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import auth, predict, history

# ─── Logging ───
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ─── Rate limiter ───
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    logger.info("🌾 Starting Rice Disease Prediction API...")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")

    # Ensure upload directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "gradcam"), exist_ok=True)
    logger.info("✅ Upload directories ready")

    # Trigger ML model loading (singleton init)
    from app.services.ml_service import ml_service
    if ml_service.demo_mode:
        logger.warning("⚠️  Running in DEMO MODE — predictions are simulated")
    else:
        logger.info("✅ ML model loaded successfully")

    logger.info("🚀 API is ready!")
    yield

    # Shutdown
    logger.info("🛑 Shutting down Rice Disease Prediction API...")


# ─── Create FastAPI App ───
app = FastAPI(
    title="Rice Leaf Disease Prediction API",
    description=(
        "AI-powered rice leaf disease classification system. "
        "Upload rice leaf images to get instant disease predictions "
        "with treatment recommendations and Grad-CAM visualizations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── Rate Limiter ───
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS Middleware ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files (for uploaded images) ───
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ─── Register Routers ───
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(history.router)


# ─── Root endpoint ───
@app.get("/", tags=["Health"])
def root():
    """API health check endpoint."""
    return {
        "status": "success",
        "data": {
            "name": "Rice Leaf Disease Prediction API",
            "version": "1.0.0",
            "docs": "/docs",
        },
        "message": "API is running",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    """Detailed health check."""
    from app.services.ml_service import ml_service
    return {
        "status": "success",
        "data": {
            "api": "healthy",
            "model_loaded": not ml_service.demo_mode,
            "demo_mode": ml_service.demo_mode,
            "storage_type": settings.STORAGE_TYPE,
        },
        "message": "All systems operational",
    }
