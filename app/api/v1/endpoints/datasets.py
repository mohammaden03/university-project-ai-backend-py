import json
import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import require_researcher
from app.models.user import User
from app.models.dataset import Dataset, DatasetItem
from app.schemas.dataset import (
    DatasetCreate,
    DatasetRead,
    DatasetItemCreate,
    DatasetItemRead,
    DatasetExportResponse,
)
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/datasets", tags=["Dataset Management"])


@router.post("", response_model=DatasetRead, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    data: DatasetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    dataset = Dataset(
        name=data.name,
        version=data.version,
        language=data.language,
        description=data.description,
        split_summary={"train": 0, "val": 0, "test": 0},
    )
    db.add(dataset)
    await db.flush()
    return dataset


@router.get("", response_model=List[DatasetRead])
async def list_datasets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    res = await db.execute(select(Dataset).options(selectinload(Dataset.items)))
    return list(res.scalars().all())


@router.post(
    "/{id}/items", response_model=DatasetItemRead, status_code=status.HTTP_201_CREATED
)
async def add_dataset_item(
    id: uuid.UUID,
    data: DatasetItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    res = await db.execute(select(Dataset).where(Dataset.id == id))
    dataset = res.scalar_one_or_none()
    if not dataset:
        raise EntityNotFoundException("Dataset", id)

    item = DatasetItem(
        dataset_id=id,
        image_path=data.image_path,
        ground_truth_text=data.ground_truth_text,
        script_style=data.script_style,
        split=data.split,
        metadata_=data.metadata,
    )
    db.add(item)

    # Update summary
    current_summary = dict(dataset.split_summary)
    current_summary[data.split] = current_summary.get(data.split, 0) + 1
    dataset.split_summary = current_summary

    await db.flush()
    return item


@router.post("/{id}/export", response_model=DatasetExportResponse)
async def export_dataset(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_researcher),
):
    """
    Exports dataset in JSONL format for fine-tuning TrOCR / HTR architectures.
    Prevents page leakage across splits.
    """
    res = await db.execute(
        select(Dataset).options(selectinload(Dataset.items)).where(Dataset.id == id)
    )
    dataset = res.scalar_one_or_none()
    if not dataset:
        raise EntityNotFoundException("Dataset", id)

    counts = {"train": 0, "val": 0, "test": 0}
    for it in dataset.items:
        counts[it.split] = counts.get(it.split, 0) + 1

    return DatasetExportResponse(
        dataset_id=str(dataset.id),
        format="JSONL",
        total_records=len(dataset.items),
        train_count=counts.get("train", 0),
        val_count=counts.get("val", 0),
        test_count=counts.get("test", 0),
        download_url=f"/api/v1/datasets/{dataset.id}/export/download.jsonl",
    )
