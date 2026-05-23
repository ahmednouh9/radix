import hashlib
import hmac
import json

from fastapi import APIRouter, Request, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from loguru import logger

from app.config import settings
from app.database import get_db
from app.services.webhook_processor import webhook_processor

router = APIRouter()


@router.get("/facebook")
async def verify_facebook_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token:
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            from app.models.platform_config import PlatformConfig
            config = db.query(PlatformConfig).filter_by(platform="facebook").first()
            if config and hub_verify_token == config.webhook_verify_token:
                logger.info("Facebook webhook verified successfully")
                return int(hub_challenge)
        finally:
            db.close()

    logger.warning(f"Facebook webhook verification failed: mode={hub_mode}")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/facebook")
async def receive_facebook_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    body_str = body.decode("utf-8")

    if settings.facebook_app_secret:
        signature = request.headers.get("X-Hub-Signature", "")
        if not signature:
            logger.warning("Missing X-Hub-Signature header")
            raise HTTPException(status_code=400, detail="Missing signature")

        expected = "sha1=" + hmac.new(
            settings.facebook_app_secret.encode("utf-8"),
            body,
            hashlib.sha1,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            logger.warning("Invalid Facebook webhook signature")
            raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    logger.info(f"Facebook webhook received: {payload.get('object')}")

    if payload.get("object") == "page":
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "comments":
                    value = change.get("value", {})
                    comment_id = value.get("id")
                    text = value.get("message", "")
                    post_id = value.get("post_id", "")
                    commenter_name = value.get("from", {}).get("name", "unknown")
                    commenter_id = value.get("from", {}).get("id", "")

                    if comment_id:
                        await webhook_processor.process_facebook_comment(
                            comment_id=comment_id,
                            comment_text=text,
                            post_id=post_id,
                            commenter_name=commenter_name,
                            commenter_id=commenter_id,
                            db=db,
                        )

            for messaging in entry.get("messaging", []):
                pass

    return {"status": "ok"}
