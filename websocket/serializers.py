"""
Message serializers
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


class WebSocketJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for WebSocket messages
    """
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, bytes):
            return obj.decode("utf-8")
        return super().default(obj)


def serialize_message(message: dict) -> str:
    """Serialize message to JSON string"""
    return json.dumps(message, cls=WebSocketJSONEncoder)


def deserialize_message(data: str) -> dict:
    """Deserialize JSON string to dict"""
    return json.loads(data)
