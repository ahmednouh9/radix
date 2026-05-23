from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ConfigBase(BaseModel):
    platform: str = Field(..., pattern="^(instagram|facebook)$")
    app_id: str
    app_secret: str
    access_token: str
    page_id: Optional[str] = None
    ig_user_id: Optional[str] = None
    webhook_verify_token: str
    is_active: bool = True
    instagram_username: Optional[str] = None
    instagram_password: Optional[str] = None


class ConfigCreate(ConfigBase):
    pass


class ConfigUpdate(BaseModel):
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    access_token: Optional[str] = None
    page_id: Optional[str] = None
    ig_user_id: Optional[str] = None
    webhook_verify_token: Optional[str] = None
    is_active: Optional[bool] = None
    instagram_username: Optional[str] = None
    instagram_password: Optional[str] = None


class ConfigOut(BaseModel):
    id: int
    platform: str
    app_id: str
    page_id: Optional[str] = None
    ig_user_id: Optional[str] = None
    webhook_verify_token: str
    is_active: bool
    last_token_refresh: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    instagram_username: Optional[str] = None

    class Config:
        from_attributes = True


class ConfigTestResult(BaseModel):
    success: bool
    message: str
    page_name: Optional[str] = None
    followers_count: Optional[int] = None
