from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationOut, NotificationList

router = APIRouter()


@router.get("/notifications", response_model=NotificationList)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform: Optional[str] = Query(None),
    type: Optional[str] = Query(None, alias="type"),
    is_read: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Notification)
    if platform:
        query = query.filter(Notification.platform == platform)
    if type:
        query = query.filter(Notification.type == type)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(desc(Notification.created_at)).offset(offset).limit(page_size).all()

    return NotificationList(
        items=[NotificationOut.model_validate(n) for n in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/notifications/{notification_id}/read", response_model=NotificationOut)
async def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


@router.post("/notifications/read-all")
async def mark_all_read(db: Session = Depends(get_db)):
    db.query(Notification).update({Notification.is_read: True})
    db.commit()
    return {"status": "ok", "message": "All notifications marked as read"}


@router.delete("/notifications/{notification_id}", status_code=204)
async def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
