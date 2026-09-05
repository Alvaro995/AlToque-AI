"""Servicio de integración con Meta WhatsApp Business Cloud API."""

import hmac
import hashlib
import logging
from typing import Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Integración empresarial con API de WhatsApp Cloud de Meta."""

    def __init__(self):
        self.verify_token = settings.whatsapp_webhook_verify_token or settings.whatsapp_verify_token
        self.api_token = settings.whatsapp_api_token or settings.whatsapp_access_token
        self.phone_number_id = settings.whatsapp_phone_number_id

    def verify_webhook_token(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Validate Meta webhook subscription challenge."""
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None

    def parse_incoming_message(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract sender phone, message text, and metadata from webhook JSON."""
        try:
            entries = payload.get("entry", [])
            if not entries:
                return None
            changes = entries[0].get("changes", [])
            if not changes:
                return None
            value = changes[0].get("value", {})
            messages = value.get("messages", [])
            if not messages:
                return None

            msg = messages[0]
            from_phone = msg.get("from")
            text_body = msg.get("text", {}).get("body", "")
            msg_id = msg.get("id")

            return {
                "from_phone": from_phone,
                "text": text_body,
                "message_id": msg_id,
                "timestamp": msg.get("timestamp"),
            }
        except Exception as e:
            logger.error(f"Failed to parse WhatsApp webhook payload: {str(e)}")
            return None

    async def send_message(self, to_phone: str, message_text: str) -> bool:
        """Send outgoing WhatsApp text message to user phone."""
        if not self.api_token or self.api_token == "mock_token":
            logger.info(f"[WhatsApp Mock Dispatch] To: {to_phone} | Content: {message_text}")
            return True

        url = f"https://graph.facebook.com/v20.0/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "text",
            "text": {"body": message_text},
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if resp.status_code in [200, 201]:
                    return True
                logger.warning(f"WhatsApp API error {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            logger.error(f"WhatsApp dispatch exception: {str(e)}")
            return False
