import asyncio
from typing import Optional, Dict, Any

import httpx
from loguru import logger

from app.config import settings

GRAPH_API_BASE = "https://graph.facebook.com"
GRAPH_API_VERSION = "v21.0"


class MetaAPIError(Exception):
    def __init__(self, message: str, status_code: int = 0, subcode: Optional[int] = None):
        self.status_code = status_code
        self.subcode = subcode
        super().__init__(message)


class RateLimitError(MetaAPIError):
    pass


class InvalidTokenError(MetaAPIError):
    pass


class MetaAPIClient:
    def __init__(self, access_token: str, platform: str):
        self.access_token = access_token
        self.platform = platform
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=f"{GRAPH_API_BASE}/{GRAPH_API_VERSION}",
                timeout=30.0,
            )
        return self._client

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        client = await self._get_client()
        url = path.lstrip("/")
        request_params = dict(params or {})
        request_params["access_token"] = self.access_token

        for attempt in range(max_retries):
            try:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    params=request_params if method.upper() == "GET" else None,
                    data=data if method.upper() == "POST" else None,
                )

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(f"Rate limited, retrying in {retry_after}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(retry_after)
                    continue

                if response.status_code == 401:
                    raise InvalidTokenError("Access token is invalid or expired", status_code=401)

                result = response.json()

                if "error" in result:
                    error = result["error"]
                    code = error.get("code", 0)
                    subcode = error.get("error_subcode", 0)
                    message = error.get("message", "Unknown Meta API error")

                    if code == 190 or code == 102:
                        raise InvalidTokenError(message, status_code=code, subcode=subcode)
                    if code == 100 and subcode == 33:
                        raise MetaAPIError(message, status_code=code, subcode=subcode)
                    if code == 368:
                        raise MetaAPIError(f"Action deemed abusive: {message}", status_code=code, subcode=subcode)
                    if code == 4 or code == 17 or code == 613:
                        raise RateLimitError(message, status_code=code, subcode=subcode)

                    raise MetaAPIError(message, status_code=code, subcode=subcode)

                return result

            except httpx.TimeoutException:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    raise MetaAPIError("Request timed out after retries", status_code=0)
                await asyncio.sleep(2 ** attempt)

            except (httpx.HTTPError, httpx.RequestError) as e:
                logger.error(f"HTTP request failed: {e}")
                raise MetaAPIError(f"HTTP request failed: {str(e)}", status_code=0)

        raise MetaAPIError("Max retries exceeded", status_code=429)

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._request("POST", path, data=data, params=params)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
