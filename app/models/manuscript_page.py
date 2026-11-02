import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ManuscriptPage(Base):
    __tablename__ = "manuscript_pages"
    __table_args__ = (
        UniqueConstraint("manuscript_id", "page_number", name="uq_manuscript_page_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    manuscript_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False
    )
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    image_path: Mapped[str] = mapped_column(String(512), nullable=False)
    image_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    processing_status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    manuscript = relationship("Manuscript", back_populates="pages")
    transcriptions = relationship("Transcription", back_populates="page", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="page", cascade="all, delete-orphan")
    ocr_jobs = relationship("OCRJob", back_populates="page")
