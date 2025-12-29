from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Content(Base):
    """
    Stores source content metadata and raw extracted text.

    Supports multiple content types: twitter, pdf, arxiv, acm, web
    """
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(50), nullable=False, index=True)  # 'twitter', 'pdf', 'arxiv', 'acm', 'web'
    source_url = Column(Text, nullable=True)  # Original URL (null for PDFs)
    file_path = Column(Text, nullable=True)  # Path to uploaded PDF (null for URLs)

    title = Column(Text, nullable=False)
    author = Column(Text, nullable=True)
    publish_date = Column(TIMESTAMP(timezone=True), nullable=True)

    raw_content = Column(Text, nullable=True)  # Full extracted text
    content_hash = Column(String(64), unique=True, index=True)  # SHA-256 for deduplication

    extraction_metadata = Column(JSON, nullable=True)  # Source-specific metadata (JSONB in PostgreSQL)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    summaries = relationship("Summary", back_populates="content", cascade="all, delete-orphan")
    content_themes = relationship("ContentTheme", back_populates="content", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Content(id={self.id}, type={self.source_type}, title='{self.title[:50]}...')>"
