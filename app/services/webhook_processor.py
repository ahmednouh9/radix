from typing import Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.platform_config import PlatformConfig
from app.models.processed_comment import ProcessedComment
from app.models.notification import Notification
from app.models.campaign import Campaign
from app.services.campaign_matcher import campaign_matcher
from app.services.instagram_api import InstagramAPI
from app.services.facebook_api import FacebookAPI
from app.services.sse_manager import sse_manager


class WebhookProcessor:
    async def process_instagram_comment(
        self,
        comment_id: str,
        comment_text: str,
        media_id: str,
        commenter_name: str,
        commenter_id: str,
        db: Session,
    ) -> Optional[ProcessedComment]:
        """Process an incoming Instagram comment through the pipeline."""
        existing = (
            db.query(ProcessedComment)
            .filter_by(platform="instagram", comment_id=comment_id)
            .first()
        )
        if existing:
            logger.info(f"Comment {comment_id} already processed, skipping")
            return existing

        config = db.query(PlatformConfig).filter_by(platform="instagram", is_active=True).first()
        if not config or not config.ig_user_id:
            logger.warning("Instagram config not found or inactive for webhook processing")
            return None

        campaign = campaign_matcher.match(comment_text, "instagram", db)

        processed = ProcessedComment(
            platform="instagram",
            comment_id=comment_id,
            media_id=media_id,
            commenter_name=commenter_name,
            commenter_id=commenter_id,
            comment_text=comment_text,
            matched_keyword=campaign.keywords.split(",")[0].strip() if campaign else None,
            campaign_id=campaign.id if campaign else None,
            status="skipped",
        )

        if not campaign:
            logger.info(f"No campaign matched for IG comment {comment_id}")
            db.add(processed)
            db.commit()
            db.refresh(processed)
            await self._create_notification(db, "comment_received", "instagram", f"New comment by {commenter_name}", comment_text[:200], comment_id, None)
            return processed

        ig_api = InstagramAPI(config.access_token, config.ig_user_id)

        try:
            reply_result = None
            dm_result = None

            if campaign.reply_text:
                try:
                    reply_result = await ig_api.reply_to_comment(comment_id, campaign.reply_text)
                    processed.reply_sent = reply_result.get("success", False)
                    processed.reply_text = campaign.reply_text
                except Exception as e:
                    logger.error(f"Failed to reply to IG comment {comment_id}: {e}")
                    processed.status = "failed"
                    processed.error_message = f"Reply failed: {str(e)}"

            if campaign.dm_text:
                try:
                    dm_result = await ig_api.send_dm(comment_id, campaign.dm_text)
                    processed.dm_sent = dm_result.get("success", False)
                    processed.dm_text = campaign.dm_text
                except Exception as e:
                    logger.error(f"Failed to DM on IG comment {comment_id}: {e}")
                    processed.status = "failed"
                    processed.error_message = (processed.error_message or "") + f" DM failed: {str(e)}"

            if processed.status != "failed":
                processed.status = "processed"

            if campaign:
                campaign.stats_total_matched = (campaign.stats_total_matched or 0) + 1

            db.add(processed)
            db.commit()
            db.refresh(processed)

            await self._create_notification(
                db,
                "reply_sent" if processed.reply_sent else "dm_sent" if processed.dm_sent else "comment_received",
                "instagram",
                f"{'Replied to' if processed.reply_sent else 'DM sent to'} {commenter_name}",
                f"Matched: {campaign.name}",
                comment_id,
                campaign.id,
            )

        except Exception as e:
            logger.error(f"Webhook processing error for IG comment {comment_id}: {e}")
            processed.status = "failed"
            processed.error_message = str(e)
            db.add(processed)
            db.commit()
        finally:
            await ig_api.close()

        return processed

    async def process_facebook_comment(
        self,
        comment_id: str,
        comment_text: str,
        post_id: str,
        commenter_name: str,
        commenter_id: str,
        db: Session,
    ) -> Optional[ProcessedComment]:
        """Process an incoming Facebook comment through the pipeline."""
        existing = (
            db.query(ProcessedComment)
            .filter_by(platform="facebook", comment_id=comment_id)
            .first()
        )
        if existing:
            return existing

        config = db.query(PlatformConfig).filter_by(platform="facebook", is_active=True).first()
        if not config or not config.page_id:
            return None

        campaign = campaign_matcher.match(comment_text, "facebook", db)

        processed = ProcessedComment(
            platform="facebook",
            comment_id=comment_id,
            media_id=post_id,
            commenter_name=commenter_name,
            commenter_id=commenter_id,
            comment_text=comment_text,
            matched_keyword=campaign.keywords.split(",")[0].strip() if campaign else None,
            campaign_id=campaign.id if campaign else None,
            status="skipped",
        )

        if not campaign:
            db.add(processed)
            db.commit()
            db.refresh(processed)
            await self._create_notification(db, "comment_received", "facebook", f"New comment by {commenter_name}", comment_text[:200], comment_id, None)
            return processed

        fb_api = FacebookAPI(config.access_token, config.page_id)

        try:
            if campaign.reply_text:
                try:
                    reply_result = await fb_api.reply_to_comment(comment_id, campaign.reply_text)
                    processed.reply_sent = reply_result.get("success", False)
                    processed.reply_text = campaign.reply_text
                except Exception as e:
                    logger.error(f"Failed to reply to FB comment {comment_id}: {e}")
                    processed.status = "failed"
                    processed.error_message = f"Reply failed: {str(e)}"

            if campaign.dm_text:
                try:
                    dm_result = await fb_api.send_dm(comment_id, campaign.dm_text)
                    processed.dm_sent = dm_result.get("success", False)
                    processed.dm_text = campaign.dm_text
                except Exception as e:
                    logger.error(f"Failed to DM on FB comment {comment_id}: {e}")
                    processed.status = "failed"
                    processed.error_message = (processed.error_message or "") + f" DM failed: {str(e)}"

            if processed.status != "failed":
                processed.status = "processed"

            if campaign:
                campaign.stats_total_matched = (campaign.stats_total_matched or 0) + 1

            db.add(processed)
            db.commit()
            db.refresh(processed)

            await self._create_notification(
                db,
                "reply_sent" if processed.reply_sent else "dm_sent" if processed.dm_sent else "comment_received",
                "facebook",
                f"{'Replied to' if processed.reply_sent else 'DM sent to'} {commenter_name}",
                f"Matched: {campaign.name}",
                comment_id,
                campaign.id,
            )

        except Exception as e:
            logger.error(f"Webhook processing error for FB comment {comment_id}: {e}")
            processed.status = "failed"
            processed.error_message = str(e)
            db.add(processed)
            db.commit()
        finally:
            await fb_api.close()

        return processed

    async def _create_notification(
        self,
        db: Session,
        notif_type: str,
        platform: str,
        title: str,
        message: str,
        comment_id: Optional[str] = None,
        campaign_id: Optional[int] = None,
    ):
        notif = Notification(
            type=notif_type,
            platform=platform,
            title=title,
            message=message,
            comment_id=comment_id,
            campaign_id=campaign_id,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        notif_dict = {
            "id": notif.id,
            "type": notif.type,
            "platform": notif.platform,
            "title": notif.title,
            "message": notif.message,
            "comment_id": notif.comment_id,
            "campaign_id": notif.campaign_id,
            "is_read": notif.is_read,
            "created_at": str(notif.created_at),
        }
        await sse_manager.broadcast({"event": "notification", "data": notif_dict})


webhook_processor = WebhookProcessor()
