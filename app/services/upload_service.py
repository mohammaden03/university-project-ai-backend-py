import uuid
from typing import Dict, Any, Tuple
from fastapi import UploadFile
from app.utils.file_validation import validate_image_upload, sanitize_filename
from app.storage.s3_storage import get_storage


class UploadService:
    @classmethod
    async def process_and_store_image(
        cls, file: UploadFile, subfolder: str = "manuscript_pages"
    ) -> Tuple[str, Dict[str, Any]]:
        # 1. Validate file format, dimensions, size
        content, metadata = await validate_image_upload(file)

        # 2. Generate safe non-colliding filename
        safe_name = sanitize_filename(file.filename or "page.jpg")

        # 3. Store via abstract storage (Local or S3/MinIO)
        storage = get_storage()
        stored_path = await storage.save(content, safe_name, subfolder=subfolder)

        metadata["stored_path"] = stored_path
        return stored_path, metadata
