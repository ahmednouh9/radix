from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base


class PlatformConfig(Base):
    __tablename__ = "platform_configs"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(20), unique=True, nullable=False)  # instagram / facebook
    app_id = Column(String(255), nullable=False)
    app_secret = Column(Text, nullable=False)
    access_token = Column(Text, nullable=False)
    page_id = Column(String(255), nullable=True)
    ig_user_id = Column(String(255), nullable=True)
    webhook_verify_token = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    last_token_refresh = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PlatformConfig(platform={self.platform}, active={self.is_active})>"
