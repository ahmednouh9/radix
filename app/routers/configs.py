from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from app.database import get_db
from app.models.platform_config import PlatformConfig
from app.schemas.config import ConfigCreate, ConfigUpdate, ConfigOut, ConfigTestResult
from app.services.instagram_api import InstagramAPI
from app.services.facebook_api import FacebookAPI

router = APIRouter()


@router.get("/configs", response_model=List[ConfigOut])
async def list_configs(db: Session = Depends(get_db)):
    return db.query(PlatformConfig).all()


@router.post("/configs", response_model=ConfigOut, status_code=201)
async def create_config(data: ConfigCreate, db: Session = Depends(get_db)):
    existing = db.query(PlatformConfig).filter(PlatformConfig.platform == data.platform).first()
    if existing:
        for field, value in data.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        logger.info(f"Config updated for {data.platform}")
        return existing
    config = PlatformConfig(**data.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)
    logger.info(f"Config created for {data.platform}")
    return config


@router.get("/configs/{platform}", response_model=ConfigOut)
async def get_config(platform: str, db: Session = Depends(get_db)):
    config = db.query(PlatformConfig).filter(PlatformConfig.platform == platform).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config


@router.put("/configs/{platform}", response_model=ConfigOut)
async def update_config(platform: str, data: ConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(PlatformConfig).filter(PlatformConfig.platform == platform).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(config, field, value)
    db.commit()
    db.refresh(config)
    logger.info(f"Config updated for {platform}")
    return config


@router.delete("/configs/{platform}", status_code=204)
async def delete_config(platform: str, db: Session = Depends(get_db)):
    config = db.query(PlatformConfig).filter(PlatformConfig.platform == platform).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    db.delete(config)
    db.commit()
    logger.info(f"Config deleted for {platform}")


@router.post("/configs/{platform}/test", response_model=ConfigTestResult)
async def test_config(platform: str, db: Session = Depends(get_db)):
    config = db.query(PlatformConfig).filter(PlatformConfig.platform == platform).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    try:
        if platform == "instagram":
            if not config.ig_user_id:
                return ConfigTestResult(success=False, message="IG User ID not configured")
            api = InstagramAPI(config.access_token, config.ig_user_id)
            info = await api.get_business_account_info()
            await api.close()
            return ConfigTestResult(
                success=True,
                message=f"Connected as @{info.get('username', 'unknown')}",
                page_name=info.get("name"),
                followers_count=info.get("followers_count"),
            )
        elif platform == "facebook":
            if not config.page_id:
                return ConfigTestResult(success=False, message="Page ID not configured")
            api = FacebookAPI(config.access_token, config.page_id)
            info = await api.get_page_info()
            await api.close()
            return ConfigTestResult(
                success=True,
                message=f"Connected to page: {info.get('name', 'unknown')}",
                page_name=info.get("name"),
                followers_count=info.get("fan_count"),
            )
    except Exception as e:
        logger.error(f"Config test failed for {platform}: {e}")
        return ConfigTestResult(success=False, message=str(e))
