from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from app.database import Base


class ProcessedComment(Base):
    __tablename__ = "processed_comments"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(20), nullable=False)
    comment_id = Column(String(255), nullable=False)
    media_id = Column(String(255), nullable=True)
    commenter_name = Column(String(255), nullable=True)
    commenter_id = Column(String(255), nullable=True)
    comment_text = Column(Text, nullable=False)
    matched_keyword = Column(String(255), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    reply_sent = Column(Boolean, default=False)
    dm_sent = Column(Boolean, default=False)
    reply_text = Column(Text, nullable=True)
    dm_text = Column(Text, nullable=True)
    status = Column(String(20), default="processed")  # processed / failed / skipped
    error_message = Column(Text, nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("platform", "comment_id", name="uq_platform_comment"),
    )

    def __repr__(self):
        return f"<ProcessedComment(platform={self.platform}, comment_id={self.comment_id})>"
