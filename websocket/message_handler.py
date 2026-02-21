"""
Handle incoming WebSocket messages
"""

import json
from typing import Any, Dict


class MessageHandler:
    """
    Process WebSocket messages
    """
    
    def __init__(self, connection_manager):
        self.manager = connection_manager
        self.handlers = {
            "subscribe": self.handle_subscribe,
            "unsubscribe": self.handle_unsubscribe,
            "ping": self.handle_ping,
            "auth": self.handle_auth,
        }
    
    async def handle_message(self, websocket, message: str):
        """Route message to appropriate handler"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            handler = self.handlers.get(msg_type)
            if handler:
                await handler(websocket, data)
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                })
        
        except json.JSONDecodeError:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid JSON",
            })
    
    async def handle_subscribe(self, websocket, data: Dict):
        """Handle subscription request"""
        symbols = data.get("symbols", [])
        await self.manager.subscribe(websocket, symbols)
    
    async def handle_unsubscribe(self, websocket, data: Dict):
        """Handle unsubscription request"""
        symbols = data.get("symbols", [])
        await self.manager.unsubscribe(websocket, symbols)
    
    async def handle_ping(self, websocket, data: Dict):
        """Handle ping"""
        await websocket.send_json({
            "type": "pong",
            "timestamp": data.get("timestamp"),
        })
    
    async def handle_auth(self, websocket, data: Dict):
        """Handle authentication"""
        token = data.get("token")
        # Validate token and associate with user
        await websocket.send_json({
            "type": "auth_response",
            "status": "success",
        })
