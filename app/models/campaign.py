from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    platform = Column(String(20), nullable=False)  # instagram / facebook
    keywords = Column(Text, nullable=False)  # comma-separated
    match_type = Column(String(20), default="contains")  # exact / contains / regex
    reply_text = Column(Text, nullable=True)
    dm_text = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    stats_total_matched = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Campaign(name={self.name}, platform={self.platform}, active={self.is_active})>"
