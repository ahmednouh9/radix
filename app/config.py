from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "change-me-in-production"
    dashboard_pin: Optional[str] = None
    instagram_app_secret: Optional[str] = None
    facebook_app_secret: Optional[str] = None
    debug: bool = False
    app_name: str = "Radix"
    app_version: str = "1.0.0"
    public_url: str = "https://web-production-be8a.up.railway.app"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
