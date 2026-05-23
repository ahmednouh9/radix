from typing import Optional, Dict, Any
from loguru import logger

from app.services.meta_api import MetaAPIClient, MetaAPIError


class InstagramAPI:
    def __init__(self, access_token: str, ig_user_id: str):
        self.client = MetaAPIClient(access_token, "instagram")
        self.ig_user_id = ig_user_id

    async def reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """
        Reply publicly to a comment.
        KNOWN BUG (April 2026): This endpoint is broken for comments by non-business users
        (error 100/subcode 33). Falls back to DM if public reply fails.
        """
        try:
            result = await self.client.post(
                f"/{comment_id}/replies",
                params={"message": message},
            )
            logger.info(f"Public reply sent to comment {comment_id}: {result}")
            return {"success": True, "method": "public_reply", "data": result}
        except MetaAPIError as e:
            if e.status_code == 100 and e.subcode == 33:
                logger.warning(f"Public reply broken for comment {comment_id}, falling back to DM. Error: {e}")
                return await self.send_dm(comment_id, message)
            raise

    async def send_dm(self, comment_id: str, message: str) -> Dict[str, Any]:
        """
        Send a private reply (DM) triggered by a comment.
        Uses recipient.comment_id which is exempt from the 24-hour messaging rule.
        """
        result = await self.client.post(
            f"/{self.ig_user_id}/messages",
            data={
                "recipient": {"comment_id": comment_id},
                "message": {"text": message},
            },
        )
        logger.info(f"DM sent for comment {comment_id}: {result}")
        return {"success": True, "method": "dm", "data": result}

    async def get_post_details(self, media_id: str) -> Dict[str, Any]:
        """Get details of a media post."""
        result = await self.client.get(
            f"/{media_id}",
            params={"fields": "id,caption,media_type,permalink,timestamp"},
        )
        return result

    async def get_business_account_info(self) -> Dict[str, Any]:
        """Get Instagram business account info."""
        result = await self.client.get(
            f"/{self.ig_user_id}",
            params={"fields": "id,username,name,profile_picture_url,followers_count"},
        )
        return result

    async def get_media_comments(self, media_id: str) -> Dict[str, Any]:
        """Get comments on a media post."""
        result = await self.client.get(
            f"/{media_id}/comments",
            params={"fields": "id,text,timestamp,username,user"},
        )
        return result

    async def close(self):
        await self.client.close()
