"""
WebSocket authentication
"""

from fastapi import WebSocket, status

from app.core.security import verify_token


class WebSocketAuth:
    """
    Handle WebSocket authentication
    """
    
    @staticmethod
    async def authenticate(websocket: WebSocket, token: str, secret_key: str) -> dict:
        """
        Authenticate WebSocket connection
        
        Returns:
            User payload if valid, raises exception otherwise
        """
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise ValueError("No token provided")
        
        try:
            payload = verify_token(token, secret_key)
            return payload
        
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise ValueError("Invalid token")
    
    @staticmethod
    async def require_auth(websocket: WebSocket, token: str = None):
        """Middleware to require authentication"""
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return False
        return True
