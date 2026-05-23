from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from loguru import logger

from app.database import get_db
from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignOut, CampaignToggle

router = APIRouter()


@router.get("/campaigns", response_model=List[CampaignOut])
async def list_campaigns(
    platform: str = Query(None),
    is_active: bool = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Campaign)
    if platform:
        query = query.filter(Campaign.platform == platform)
    if is_active is not None:
        query = query.filter(Campaign.is_active == is_active)
    return query.order_by(Campaign.created_at.desc()).all()


@router.post("/campaigns", response_model=CampaignOut, status_code=201)
async def create_campaign(data: CampaignCreate, db: Session = Depends(get_db)):
    campaign = Campaign(**data.model_dump())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    logger.info(f"Campaign created: {campaign.name} ({campaign.platform})")
    return campaign


@router.get("/campaigns/{campaign_id}", response_model=CampaignOut)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/campaigns/{campaign_id}", response_model=CampaignOut)
async def update_campaign(campaign_id: int, data: CampaignUpdate, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    db.commit()
    db.refresh(campaign)
    logger.info(f"Campaign updated: {campaign.name}")
    return campaign


@router.delete("/campaigns/{campaign_id}", status_code=204)
async def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    db.delete(campaign)
    db.commit()
    logger.info(f"Campaign deleted: {campaign.name}")


@router.patch("/campaigns/{campaign_id}/toggle", response_model=CampaignToggle)
async def toggle_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.is_active = not campaign.is_active
    db.commit()
    db.refresh(campaign)
    logger.info(f"Campaign '{campaign.name}' toggled to {campaign.is_active}")
    return CampaignToggle(is_active=campaign.is_active)
