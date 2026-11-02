import os
import uuid
from typing import Tuple
from PIL import Image
from fastapi import UploadFile
from app.core.config import get_settings
from app.core.exceptions import FileValidationException

settings = get_settings()

MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def sanitize_filename(filename: str) -> str:
    """Removes path traversal characters and generates unique safe filename."""
    base = os.path.basename(filename)
    clean_name = "".join(c for c in base if c.isalnum() or c in "._- ")
    ext = os.path.splitext(clean_name)[1].lower()
    unique_prefix = uuid.uuid4().hex
    return f"{unique_prefix}{ext}"


async def validate_image_upload(file: UploadFile) -> Tuple[bytes, dict]:
    """
    Validates file extension, size, and reads image dimensions via Pillow.
    Returns image bytes and metadata dictionary.
    """
    if not file.filename:
        raise FileValidationException("Uploaded file has no filename.")

    ext = os.path.splitext(file.filename)[1].lstrip(".").lower()
    if ext not in settings.allowed_extensions_set:
        raise FileValidationException(
            f"Invalid file extension '{ext}'. Allowed extensions: {list(settings.allowed_extensions_set)}"
        )

    # Read contents into memory
    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise FileValidationException("Uploaded file is empty.")

    if file_size > MAX_BYTES:
        raise FileValidationException(
            f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # Validate image integrity and dimensions using Pillow
    try:
        import io
        with Image.open(io.BytesIO(content)) as img:
            img.verify()
        
        # Re-open for metadata reading as verify() closes the stream
        with Image.open(io.BytesIO(content)) as img:
            width, height = img.size
            format_name = img.format or ext.upper()
            mode = img.mode

            if width < 50 or height < 50:
                raise FileValidationException(
                    f"Image dimensions ({width}x{height}) are too small for manuscript recognition."
                )

            metadata = {
                "original_filename": file.filename,
                "file_size_bytes": file_size,
                "width": width,
                "height": height,
                "format": format_name,
                "mode": mode,
            }
            return content, metadata

    except Exception as e:
        if isinstance(e, FileValidationException):
            raise e
        raise FileValidationException(f"Invalid or corrupted image file: {str(e)}")
