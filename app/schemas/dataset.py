import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class DatasetCreate(BaseModel):
    name: str
    version: str = "1.0.0"
    language: str = "fa"
    description: Optional[str] = None


class DatasetItemCreate(BaseModel):
    image_path: str
    ground_truth_text: str
    script_style: Optional[str] = "Naskh"
    split: str = "train"  # "train", "val", "test"
    metadata: Dict[str, Any] = {}


class DatasetItemRead(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    image_path: str
    ground_truth_text: str
    script_style: Optional[str] = None
    split: str
    metadata_: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetRead(BaseModel):
    id: uuid.UUID
    name: str
    version: str
    language: str
    description: Optional[str] = None
    split_summary: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    items: List[DatasetItemRead] = []

    class Config:
        from_attributes = True


class DatasetExportResponse(BaseModel):
    dataset_id: str
    format: str = "JSONL"
    total_records: int
    train_count: int
    val_count: int
    test_count: int
    download_url: str
