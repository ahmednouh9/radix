from typing import Optional, Dict, Any
from loguru import logger

from app.services.meta_api import MetaAPIClient


class FacebookAPI:
    def __init__(self, access_token: str, page_id: str):
        self.client = MetaAPIClient(access_token, "facebook")
        self.page_id = page_id

    async def reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """Reply publicly to a Facebook comment."""
        result = await self.client.post(
            f"/{comment_id}",
            params={"message": message},
        )
        logger.info(f"Public reply sent to FB comment {comment_id}: {result}")
        return {"success": True, "method": "public_reply", "data": result}

    async def send_dm(self, comment_id: str, message: str) -> Dict[str, Any]:
        """
        Send a private reply via Messenger.
        Private Reply API is exempt from the 24-hour messaging rule when triggered by a comment.
        """
        result = await self.client.post(
            f"/{self.page_id}/messages",
            data={
                "recipient": {"comment_id": comment_id},
                "message": {"text": message},
            },
        )
        logger.info(f"DM sent for FB comment {comment_id}: {result}")
        return {"success": True, "method": "dm", "data": result}

    async def get_post_details(self, post_id: str) -> Dict[str, Any]:
        """Get details of a Facebook post."""
        result = await self.client.get(
            f"/{post_id}",
            params={"fields": "id,message,permalink_url,created_time"},
        )
        return result

    async def get_page_info(self) -> Dict[str, Any]:
        """Get Facebook Page info."""
        result = await self.client.get(
            f"/{self.page_id}",
            params={"fields": "id,name,username,fan_count,picture"},
        )
        return result

    async def get_post_comments(self, post_id: str) -> Dict[str, Any]:
        """Get comments on a Facebook post."""
        result = await self.client.get(
            f"/{post_id}/comments",
            params={"fields": "id,message,from,created_time"},
        )
        return result

    async def close(self):
        await self.client.close()
