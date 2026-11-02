import io
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.manuscript import ManuscriptPageRead
from app.services.upload_service import UploadService
from app.services.manuscript_service import ManuscriptService
from app.storage.s3_storage import get_storage

router = APIRouter(tags=["Pages and Uploads"])


@router.post("/uploads", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    stored_path, metadata = await UploadService.process_and_store_image(file)
    return {
        "status": "success",
        "file_path": stored_path,
        "metadata": metadata,
    }


@router.post(
    "/manuscripts/{id}/pages",
    response_model=ManuscriptPageRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_manuscript_page(
    id: uuid.UUID,
    file: UploadFile = File(...),
    page_number: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stored_path, metadata = await UploadService.process_and_store_image(
        file, subfolder=f"manuscripts/{id}"
    )
    service = ManuscriptService(db)
    page = await service.add_page_to_manuscript(
        manuscript_id=id,
        image_path=stored_path,
        image_metadata=metadata,
        page_number=page_number,
    )
    return page


@router.get("/pages/{id}", response_model=ManuscriptPageRead)
async def get_manuscript_page(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ManuscriptService(db)
    page = await service.get_page(id)
    return page


@router.get("/pages/{id}/image")
async def get_page_image_binary(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Controlled and authenticated streaming of original manuscript image binary.
    Guards high-resolution archival images against unauthorized public scraping.
    """
    service = ManuscriptService(db)
    page = await service.get_page(id)

    storage = get_storage()
    image_bytes = await storage.read(page.image_path)

    media_type = page.image_metadata.get("format", "jpeg").lower()
    if media_type == "jpg":
        media_type = "jpeg"

    return Response(content=image_bytes, media_type=f"image/{media_type}")
