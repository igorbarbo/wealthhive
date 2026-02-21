"""
WebSocket exceptions
"""


class WebSocketException(Exception):
    """Base WebSocket exception"""
    pass


class ConnectionClosed(WebSocketException):
    """Connection closed unexpectedly"""
    pass


class RateLimitExceeded(WebSocketException):
    """Rate limit exceeded"""
    pass


class AuthenticationFailed(WebSocketException):
    """Authentication failed"""
    pass


class InvalidMessage(WebSocketException):
    """Invalid message format"""
    pass
  
