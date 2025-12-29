from sqlalchemy import Column, Integer, Float, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ContentTheme(Base):
    """
    Many-to-many relationship between content and themes.

    Includes confidence score for each categorization.
    """
    __tablename__ = "content_themes"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False, index=True)
    theme_id = Column(Integer, ForeignKey("themes.id", ondelete="CASCADE"), nullable=False, index=True)

    confidence = Column(Float, nullable=True)  # Categorization confidence score (0.0 to 1.0)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    content = relationship("Content", back_populates="content_themes")
    theme = relationship("Theme", back_populates="content_themes")

    # Unique constraint: one content cannot have the same theme twice
    __table_args__ = (
        UniqueConstraint('content_id', 'theme_id', name='uix_content_theme'),
    )

    def __repr__(self):
        return f"<ContentTheme(content_id={self.content_id}, theme_id={self.theme_id}, confidence={self.confidence})>"
