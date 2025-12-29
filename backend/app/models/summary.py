from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Summary(Base):
    """
    Stores AI-generated summaries for content.

    Includes structured fields: overview, key insights, implications
    """
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False, index=True)

    summary_type = Column(String(50), default="comprehensive")  # For future: 'brief', 'technical', etc.

    overview = Column(Text, nullable=False)  # Method/approach overview
    key_insights = Column(ARRAY(Text), nullable=False)  # Array of key insights
    implications = Column(Text, nullable=True)  # Discussion/implications

    generated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    model_version = Column(String(50), nullable=True)  # Claude model used
    token_count = Column(Integer, nullable=True)  # For cost tracking

    # Relationships
    content = relationship("Content", back_populates="summaries")

    def __repr__(self):
        return f"<Summary(id={self.id}, content_id={self.content_id}, type={self.summary_type})>"
