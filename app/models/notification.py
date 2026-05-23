from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # comment_received / reply_sent / dm_sent / error
    platform = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    comment_id = Column(String(255), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notification(type={self.type}, platform={self.platform}, read={self.is_read})>"
