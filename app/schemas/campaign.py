from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    platform: str = Field(..., pattern="^(instagram|facebook)$")
    keywords: str = Field(..., min_length=1)
    match_type: str = Field(default="contains", pattern="^(exact|contains|regex)$")
    reply_text: Optional[str] = None
    dm_text: Optional[str] = None
    is_active: bool = True


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    platform: Optional[str] = Field(None, pattern="^(instagram|facebook)$")
    keywords: Optional[str] = None
    match_type: Optional[str] = Field(None, pattern="^(exact|contains|regex)$")
    reply_text: Optional[str] = None
    dm_text: Optional[str] = None
    is_active: Optional[bool] = None


class CampaignOut(CampaignBase):
    id: int
    stats_total_matched: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignToggle(BaseModel):
    is_active: bool
