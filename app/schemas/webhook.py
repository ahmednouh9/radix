from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class WebhookVerification(BaseModel):
    hub_mode: str
    hub_verify_token: str
    hub_challenge: str


class WebhookEntry(BaseModel):
    id: str
    time: Optional[int] = None
    changes: Optional[List[Dict[str, Any]]] = None
    messaging: Optional[List[Dict[str, Any]]] = None


class WebhookPayload(BaseModel):
    object: str
    entry: List[WebhookEntry]
