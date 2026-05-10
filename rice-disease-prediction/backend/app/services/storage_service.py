"""
Storage service — abstraction layer for image storage.

Supports local filesystem and AWS S3. Configurable via STORAGE_TYPE env var.
"""

import os
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService(ABC):
    """Abstract base for storage backends."""

    @abstractmethod
    def upload_image(self, file_bytes: bytes, filename: str, folder: str = "images") -> str:
        """Upload image bytes and return the URL/path."""
        pass

    @abstractmethod
    def delete_image(self, url: str) -> bool:
        """Delete an image by URL. Returns True on success."""
        pass

    @abstractmethod
    def get_url(self, path: str) -> str:
        """Get the full URL for a stored file."""
        pass


class LocalStorageService(StorageService):
    """Store images on the local filesystem under UPLOAD_DIR."""

    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload_image(self, file_bytes: bytes, filename: str, folder: str = "images") -> str:
        """Save file to local disk and return the relative URL path."""
        # Create subfolder
        folder_path = os.path.join(self.upload_dir, folder)
        os.makedirs(folder_path, exist_ok=True)

        # Generate unique filename
        ext = os.path.splitext(filename)[1] or ".png"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(folder_path, unique_name)

        # Write file
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Return URL path (served by FastAPI static files)
        url_path = f"/uploads/{folder}/{unique_name}"
        logger.info(f"Saved image to {file_path} → {url_path}")
        return url_path

    def delete_image(self, url: str) -> bool:
        """Delete a locally stored image."""
        try:
            # Convert URL path to filesystem path
            relative = url.lstrip("/")
            file_path = os.path.join(".", relative)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete {url}: {e}")
            return False

    def get_url(self, path: str) -> str:
        return path


class S3StorageService(StorageService):
    """Store images in AWS S3."""

    def __init__(self):
        try:
            import boto3
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            self.bucket = settings.S3_BUCKET_NAME
            self.region = settings.AWS_REGION
            logger.info(f"S3 storage initialized: {self.bucket}")
        except Exception as e:
            logger.error(f"Failed to initialize S3: {e}")
            raise

    def upload_image(self, file_bytes: bytes, filename: str, folder: str = "images") -> str:
        """Upload to S3 and return the public URL."""
        ext = os.path.splitext(filename)[1] or ".png"
        key = f"{folder}/{uuid.uuid4().hex}{ext}"

        content_type = "image/jpeg" if ext.lower() in [".jpg", ".jpeg"] else "image/png"

        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )

        url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
        logger.info(f"Uploaded to S3: {url}")
        return url

    def delete_image(self, url: str) -> bool:
        """Delete from S3."""
        try:
            # Extract key from URL
            prefix = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/"
            key = url.replace(prefix, "")
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception as e:
            logger.error(f"S3 delete failed: {e}")
            return False

    def get_url(self, path: str) -> str:
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{path}"


def get_storage_service() -> StorageService:
    """Factory: returns the configured storage backend."""
    if settings.STORAGE_TYPE == "s3":
        return S3StorageService()
    return LocalStorageService()


# Singleton instance
storage_service = get_storage_service()
