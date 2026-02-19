"""
WealthHive - Main Application Entry Point
FastAPI application with comprehensive middleware and event handlers
"""

import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import (
    assets,
    auth,
    backtests,
    ml,
    nlp,
    orders,
    portfolios,
    quant,
    reports,
    users,
    websocket,
)
from app.config import Settings, get_settings
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.core.middleware import LoggingMiddleware, RateLimitMiddleware

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    settings = get_settings()
    logger.info("Starting up WealthHive API...", environment=settings.ENVIRONMENT)
    
    # Startup
    await create_start_app_handler(app)()
    
    yield
    
    # Shutdown
    await create_stop_app_handler(app)()
    logger.info("Shutting down WealthHive API...")


def create_application() -> FastAPI:
    """Application factory pattern"""
    settings = get_settings()
    
    app = FastAPI(
        title="WealthHive API",
        description="Quantitative Investment Management Platform",
        version="1.0.0",
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/api/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
    
    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", error=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
    
    # Health check
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": time.time(),
        }
    
    # API Routes v1
    api_v1_prefix = "/api/v1"
    
    app.include_router(auth.router, prefix=f"{api_v1_prefix}/auth", tags=["Authentication"])
    app.include_router(users.router, prefix=f"{api_v1_prefix}/users", tags=["Users"])
    app.include_router(assets.router, prefix=f"{api_v1_prefix}/assets", tags=["Assets"])
    app.include_router(portfolios.router, prefix=f"{api_v1_prefix}/portfolios", tags=["Portfolios"])
    app.include_router(orders.router, prefix=f"{api_v1_prefix}/orders", tags=["Orders"])
    app.include_router(backtests.router, prefix=f"{api_v1_prefix}/backtests", tags=["Backtests"])
    app.include_router(ml.router, prefix=f"{api_v1_prefix}/ml", tags=["Machine Learning"])
    app.include_router(nlp.router, prefix=f"{api_v1_prefix}/nlp", tags=["NLP"])
    app.include_router(quant.router, prefix=f"{api_v1_prefix}/quant", tags=["Quantitative"])
    app.include_router(reports.router, prefix=f"{api_v1_prefix}/reports", tags=["Reports"])
    app.include_router(websocket.router, prefix=f"{api_v1_prefix}/ws", tags=["WebSocket"])
    
    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.API_WORKERS,
    )
  
