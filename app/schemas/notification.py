from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    type: str
    platform: str
    title: str
    message: str
    comment_id: Optional[str] = None
    campaign_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    items: List[NotificationOut]
    total: int
    page: int
    page_size: int
