from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
# from pgvector.sqlalchemy import Vector  # Optional - not installed
from app.database import Base


class Theme(Base):
    """
    Stores research themes/categories.

    Themes emerge organically. Embeddings are optional (not currently used).
    """
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color for UI (e.g., '#FF5733')

    # Vector embedding for semantic similarity (optional - not currently used)
    # embedding = Column(Vector(1536), nullable=True)

    content_count = Column(Integer, default=0)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    content_themes = relationship("ContentTheme", back_populates="theme", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Theme(id={self.id}, name='{self.name}', count={self.content_count})>"
