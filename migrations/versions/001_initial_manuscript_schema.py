"""Initial manuscript schema with pgvector and full-text indexes

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-31 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector and pg_trgm extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # 2. Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, default='USER'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 3. Authors table
    op.create_table(
        'authors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('full_name', sa.String(length=255), nullable=False, index=True),
        sa.Column('alternative_names', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('biography', sa.Text(), nullable=True),
        sa.Column('birth_date', sa.String(length=100), nullable=True),
        sa.Column('death_date', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 4. Books table
    op.create_table(
        'books',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False, index=True),
        sa.Column('alternative_titles', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('authors.id', ondelete='SET NULL'), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=False, default='fa'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('publication_period', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 5. Manuscripts table
    op.create_table(
        'manuscripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('book_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('books.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False, index=True),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('authors.id', ondelete='SET NULL'), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=False, default='fa'),
        sa.Column('script_style', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('collection_name', sa.String(length=255), nullable=True),
        sa.Column('catalog_reference', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 6. ManuscriptPages table
    op.create_table(
        'manuscript_pages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('manuscript_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manuscripts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('image_path', sa.String(length=512), nullable=False),
        sa.Column('image_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('processing_status', sa.String(length=50), nullable=False, default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('manuscript_id', 'page_number', name='uq_manuscript_page_number')
    )

    # 7. Transcriptions table
    op.create_table(
        'transcriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('manuscript_page_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manuscript_pages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('original_recognized_text', sa.Text(), nullable=False),
        sa.Column('corrected_text', sa.Text(), nullable=True),
        sa.Column('normalized_text', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, default='fa'),
        sa.Column('model_name', sa.String(length=150), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('recognition_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('verification_status', sa.String(length=50), nullable=False, default='PENDING'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 8. ChatConversations table
    op.create_table(
        'chat_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('mode', sa.String(length=50), nullable=False, default='RESEARCH'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 9. ChatMessages table
    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 10. OCRJobs table
    op.create_table(
        'ocr_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('manuscript_page_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manuscript_pages.id', ondelete='SET NULL'), nullable=True),
        sa.Column('uploaded_file_path', sa.String(length=512), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='QUEUED'),
        sa.Column('progress', sa.Float(), nullable=False, default=0.0),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )

    # 11. Embeddings table with pgvector column
    op.create_table(
        'embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('transcription_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transcriptions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('manuscript_page_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manuscript_pages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('normalized_text', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(768), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 12. Datasets & Dataset Items table
    op.create_table(
        'datasets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False, default='1.0.0'),
        sa.Column('language', sa.String(length=10), nullable=False, default='fa'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('split_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'dataset_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('image_path', sa.String(length=512), nullable=False),
        sa.Column('ground_truth_text', sa.Text(), nullable=False),
        sa.Column('script_style', sa.String(length=100), nullable=True),
        sa.Column('split', sa.String(length=20), nullable=False, default='train'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 13. Create Indexes for High Performance Search
    # Full text search index on transcriptions normalized_text using GIN
    op.execute("CREATE INDEX idx_transcriptions_normalized_text_trgm ON transcriptions USING gin (normalized_text gin_trgm_ops);")
    op.execute("CREATE INDEX idx_embeddings_normalized_text_trgm ON embeddings USING gin (normalized_text gin_trgm_ops);")
    op.execute("CREATE INDEX idx_books_title_trgm ON books USING gin (title gin_trgm_ops);")
    op.execute("CREATE INDEX idx_authors_name_trgm ON authors USING gin (full_name gin_trgm_ops);")
    
    # Vector index for cosine distance similarity
    op.execute("CREATE INDEX idx_embeddings_vector_cosine ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);")


def downgrade() -> None:
    op.drop_table('dataset_items')
    op.drop_table('datasets')
    op.drop_table('embeddings')
    op.drop_table('ocr_jobs')
    op.drop_table('chat_messages')
    op.drop_table('chat_conversations')
    op.drop_table('transcriptions')
    op.drop_table('manuscript_pages')
    op.drop_table('manuscripts')
    op.drop_table('books')
    op.drop_table('authors')
    op.drop_table('users')
