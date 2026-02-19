"""
WebSocket endpoints for real-time data
"""

from typing import Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

from app.config import Settings, get_settings
from app.dependencies import get_current_user_ws
from websocket.connection_manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/market-data")
async def market_data_websocket(
    websocket: WebSocket,
    token: str = None,
    settings: Settings = Depends(get_settings),
):
    """WebSocket for real-time market data"""
    if not settings.ENABLE_REALTIME_WEBSOCKET:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Authenticate
    if token:
        try:
            user = await get_current_user_ws(token, settings)
            await manager.connect(websocket, user_id=user["id"])
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    else:
        await manager.connect(websocket, user_id=None)
    
    try:
        while True:
            # Receive subscription message
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "subscribe":
                symbols = data.get("symbols", [])
                await manager.subscribe(websocket, symbols)
                await websocket.send_json({
                    "type": "subscribed",
                    "symbols": symbols,
                })
            
            elif action == "unsubscribe":
                symbols = data.get("symbols", [])
                await manager.unsubscribe(websocket, symbols)
            
            elif action == "ping":
                await websocket.send_json({"type": "pong", "timestamp": data.get("timestamp")})
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


@router.websocket("/portfolio/{portfolio_id}")
async def portfolio_websocket(
    websocket: WebSocket,
    portfolio_id: str,
    token: str = None,
    settings: Settings = Depends(get_settings),
):
    """WebSocket for real-time portfolio updates"""
    if not settings.ENABLE_REALTIME_WEBSOCKET:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Must be authenticated
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    try:
        user = await get_current_user_ws(token, settings)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Verify portfolio ownership
    # ... validation logic ...
    
    await manager.connect(websocket, user_id=user["id"], portfolio_id=portfolio_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            # Handle portfolio-specific actions
            await websocket.send_json({"type": "ack", "received": data})
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


@router.post("/broadcast", response_model=dict)
async def broadcast_message(
    message: dict,
    channel: str = "all",
    settings: Settings = Depends(get_settings),
) -> Any:
    """Admin endpoint to broadcast message to all connected clients"""
    await manager.broadcast(message, channel=channel)
    return {
        "status": "broadcasted",
        "channel": channel,
        "connected_clients": len(manager.active_connections),
    }
  
