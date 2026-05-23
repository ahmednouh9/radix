import hashlib
import hmac
import json
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from loguru import logger

from app.config import settings
from app.database import get_db
from app.services.webhook_processor import webhook_processor

router = APIRouter()


@router.get("/instagram")
async def verify_instagram_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    request: Request = None,
):
    if hub_mode == "subscribe" and hub_verify_token:
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            from app.models.platform_config import PlatformConfig
            config = db.query(PlatformConfig).filter_by(platform="instagram").first()
            if config and hub_verify_token == config.webhook_verify_token:
                logger.info("Instagram webhook verified successfully")
                return int(hub_challenge)
        finally:
            db.close()

    logger.warning(f"Instagram webhook verification failed: mode={hub_mode}, token={hub_verify_token}")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/instagram")
async def receive_instagram_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    body_str = body.decode("utf-8")

    if settings.instagram_app_secret:
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not signature:
            logger.warning("Missing X-Hub-Signature-256 header")
            raise HTTPException(status_code=400, detail="Missing signature")

        expected = "sha256=" + hmac.new(
            settings.instagram_app_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            logger.warning("Invalid Instagram webhook signature")
            raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    logger.info(f"Instagram webhook received: {payload.get('object')}")

    if payload.get("object") == "instagram":
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "comments":
                    value = change.get("value", {})
                    comment_id = value.get("id")
                    text = value.get("text", "")
                    media_id = value.get("media_id", "")
                    commenter_name = value.get("from", {}).get("username", "unknown")
                    commenter_id = value.get("from", {}).get("id", "")

                    if comment_id:
                        await webhook_processor.process_instagram_comment(
                            comment_id=comment_id,
                            comment_text=text,
                            media_id=media_id,
                            commenter_name=commenter_name,
                            commenter_id=commenter_id,
                            db=db,
                        )

    return {"status": "ok"}
