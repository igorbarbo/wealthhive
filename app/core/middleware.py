"""
FastAPI middleware components
"""

import time
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query=str(request.query_params),
            client=request.client.host if request.client else None,
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(process_time * 1000, 2),
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(process_time * 1000, 2),
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        # Get client identifier
        client_id = request.headers.get("X-API-Key") or request.client.host
        
        # Check rate limit (simplified - would use Redis in production)
        # Implementation would check Redis for request count
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        return response
