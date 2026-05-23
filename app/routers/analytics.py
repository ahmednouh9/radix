from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, Integer

from app.database import get_db
from app.models.processed_comment import ProcessedComment
from app.models.campaign import Campaign
from app.models.notification import Notification

router = APIRouter()


@router.get("/analytics/overview")
async def analytics_overview(db: Session = Depends(get_db)):
    total_processed = db.query(ProcessedComment).count()
    total_replies = db.query(ProcessedComment).filter(ProcessedComment.reply_sent == True).count()
    total_dms = db.query(ProcessedComment).filter(ProcessedComment.dm_sent == True).count()
    total_failed = db.query(ProcessedComment).filter(ProcessedComment.status == "failed").count()
    total_skipped = db.query(ProcessedComment).filter(ProcessedComment.status == "skipped").count()
    active_campaigns = db.query(Campaign).filter(Campaign.is_active == True).count()
    total_campaigns = db.query(Campaign).count()

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = db.query(ProcessedComment).filter(ProcessedComment.processed_at >= today_start).count()

    unread_notifications = db.query(Notification).filter(Notification.is_read == False).count()

    return {
        "total_processed": total_processed,
        "total_replies": total_replies,
        "total_dms": total_dms,
        "total_failed": total_failed,
        "total_skipped": total_skipped,
        "today_count": today_count,
        "active_campaigns": active_campaigns,
        "total_campaigns": total_campaigns,
        "unread_notifications": unread_notifications,
        "success_rate": round((total_replies + total_dms) / max(total_processed, 1) * 100, 1),
    }


@router.get("/analytics/timeline")
async def analytics_timeline(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            cast(ProcessedComment.processed_at, Date).label("date"),
            func.count().label("total"),
            func.sum(cast(ProcessedComment.reply_sent, Integer)).label("replies"),
            func.sum(cast(ProcessedComment.dm_sent, Integer)).label("dms"),
        )
        .filter(ProcessedComment.processed_at >= since)
        .group_by(cast(ProcessedComment.processed_at, Date))
        .order_by("date")
        .all()
    )

    result = []
    for row in rows:
        result.append({
            "date": str(row.date),
            "total": row.total,
            "replies": row.replies or 0,
            "dms": row.dms or 0,
        })
    return result


@router.get("/analytics/by-campaign")
async def analytics_by_campaign(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).all()
    result = []
    for campaign in campaigns:
        count = (
            db.query(ProcessedComment)
            .filter(ProcessedComment.campaign_id == campaign.id)
            .count()
        )
        result.append({
            "id": campaign.id,
            "name": campaign.name,
            "platform": campaign.platform,
            "is_active": campaign.is_active,
            "total_matched": count,
        })
    return result
