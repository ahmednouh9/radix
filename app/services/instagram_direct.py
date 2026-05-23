import asyncio
from typing import Optional
from loguru import logger
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError


class InstagramDirectClient:
    def __init__(self):
        self._client: Optional[Client] = None
        self._logged_in = False
        self._username: Optional[str] = None

    @property
    def is_logged_in(self) -> bool:
        return self._logged_in and self._client is not None

    async def login(self, username: str, password: str) -> bool:
        if self._logged_in and self._username == username:
            return True
        try:
            cl = Client()

            def _login():
                cl.login(username, password)
                return cl

            self._client = await asyncio.to_thread(_login)
            self._logged_in = True
            self._username = username
            logger.info(f"Logged into Instagram as @{username}")
            return True
        except LoginRequired as e:
            logger.error(f"Instagram login failed (bad credentials) for @{username}: {e}")
            self._logged_in = False
            raise
        except ClientError as e:
            logger.error(f"Instagram login error for @{username}: {e}")
            self._logged_in = False
            raise
        except Exception as e:
            logger.error(f"Unexpected Instagram login error for @{username}: {e}")
            self._logged_in = False
            raise

    async def reply_to_comment(self, media_id: str, comment_id: str, text: str) -> dict:
        if not self.is_logged_in:
            raise RuntimeError("Not logged into Instagram")
        try:
            def _reply():
                return self._client.comment_reply(media_id, comment_id, text)
            result = await asyncio.to_thread(_reply)
            return {"success": True, "id": str(result.id) if hasattr(result, 'id') else None}
        except Exception as e:
            logger.error(f"Failed to reply to comment {comment_id} on media {media_id}: {e}")
            raise

    async def send_dm(self, user_id: str, text: str) -> dict:
        if not self.is_logged_in:
            raise RuntimeError("Not logged into Instagram")
        try:
            def _dm():
                return self._client.direct_send(text, [user_id])
            result = await asyncio.to_thread(_dm)
            return {"success": True, "id": str(result.id) if hasattr(result, 'id') else None}
        except Exception as e:
            logger.error(f"Failed to send DM to user {user_id}: {e}")
            raise

    async def comment_on_media(self, media_id: str, text: str) -> dict:
        if not self.is_logged_in:
            raise RuntimeError("Not logged into Instagram")
        try:
            def _comment():
                return self._client.media_comment(media_id, text)
            result = await asyncio.to_thread(_comment)
            return {"success": True, "id": str(result.id) if hasattr(result, 'id') else None}
        except Exception as e:
            logger.error(f"Failed to comment on media {media_id}: {e}")
            raise

    async def get_media_comments(self, media_id: str) -> list:
        if not self.is_logged_in:
            raise RuntimeError("Not logged into Instagram")
        try:
            def _get_comments():
                comments = self._client.media_comments(media_id)
                result = []
                for c in comments:
                    result.append({
                        "id": str(c.id),
                        "text": c.text,
                        "user_id": str(c.user.pk),
                        "username": c.user.username,
                        "created_at": str(c.created_at_utc),
                    })
                return result
            return await asyncio.to_thread(_get_comments)
        except Exception as e:
            logger.error(f"Failed to get comments for media {media_id}: {e}")
            raise

    async def get_user_medias(self, username: str, count: int = 10) -> list:
        if not self.is_logged_in:
            raise RuntimeError("Not logged into Instagram")
        try:
            def _get_medias():
                user_id = self._client.user_id_from_username(username)
                medias = self._client.user_medias(user_id, count)
                result = []
                for m in medias:
                    result.append({
                        "id": str(m.id),
                        "code": m.code,
                        "caption": m.caption_text if m.caption_text else "",
                        "comment_count": m.comment_count,
                        "like_count": m.like_count,
                        "taken_at": str(m.taken_at),
                        "media_type": m.media_type,
                    })
                return result
            return await asyncio.to_thread(_get_medias)
        except Exception as e:
            logger.error(f"Failed to get medias for user {username}: {e}")
            raise

    async def get_user_id_from_username(self, username: str) -> str:
        if not self.is_logged_in:
            raise RuntimeError("Not logged into Instagram")
        try:
            def _get_id():
                return str(self._client.user_id_from_username(username))
            return await asyncio.to_thread(_get_id)
        except Exception as e:
            logger.error(f"Failed to get user ID for {username}: {e}")
            raise

    async def close(self):
        if self._client:
            try:
                def _logout():
                    self._client.logout()
                await asyncio.to_thread(_logout)
            except Exception:
                pass
            self._client = None
            self._logged_in = False
            self._username = None


instagram_direct_client = InstagramDirectClient()