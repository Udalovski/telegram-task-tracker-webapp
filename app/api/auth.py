import hmac
import hashlib
import json
import urllib.parse
from typing import Optional, Dict, Any
import logging
from fastapi import Header, Query, HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


def validate_telegram_init_data(init_data: str, bot_token: str) -> Optional[Dict[str, Any]]:
    """
    Validate Telegram WebApp initData cryptographic signature.
    Returns parsed user data dictionary if valid, None otherwise.
    """
    try:
        parsed_data = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
        if "hash" not in parsed_data:
            return None

        received_hash = parsed_data.pop("hash")

        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))


        secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

        if hmac.compare_digest(computed_hash, received_hash):
            if "user" in parsed_data:
                user_info = json.loads(parsed_data["user"])
                return user_info
            return parsed_data
        return None
    except Exception as e:
        logger.warning(f"Error validating initData: {e}")
        return None


async def get_current_telegram_user(
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data"),
    telegram_id: Optional[int] = Query(None)
) -> Dict[str, Any]:
    """
    Dependency to authenticate user from Telegram WebApp initData
    or fallback to telegram_id for browser development / direct preview.
    """
    if x_telegram_init_data:
        user_info = validate_telegram_init_data(x_telegram_init_data, settings.BOT_TOKEN)
        if user_info and "id" in user_info:
            return user_info


    if telegram_id:
        return {
            "id": telegram_id,
            "first_name": "Authentication error",
            "username": None
        }


    return {
        "id": 1,
        "first_name": "Authentication error",
        "username": "mariia"
    }
