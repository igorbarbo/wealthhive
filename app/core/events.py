"""
Application lifecycle events
"""

from typing import Callable

import structlog

from infrastructure.cache.redis_client import RedisCache
from infrastructure.database.connection import AsyncDatabaseManager

logger = structlog.get_logger()


def create_start_app_handler(app) -> Callable:
    """Create startup event handler"""
    async def start_app() -> None:
        logger.info("Initializing application...")
        
        # Initialize database
        db_manager = AsyncDatabaseManager()
        await db_manager.initialize()
        logger.info("Database initialized")
        
        # Initialize Redis
        cache = RedisCache()
        await cache.connect()
        logger.info("Cache connected")
        
        # Load ML models
        # from ml.inference.model_registry import ModelRegistry
        # registry = ModelRegistry()
        # await registry.load_models()
        # logger.info("ML models loaded")
        
        logger.info("Application startup complete")
    
    return start_app


def create_stop_app_handler(app) -> Callable:
    """Create shutdown event handler"""
    async def stop_app() -> None:
        logger.info("Shutting down application...")
        
        # Close database connections
        db_manager = AsyncDatabaseManager()
        await db_manager.close()
        logger.info("Database connections closed")
        
        # Close Redis
        cache = RedisCache()
        await cache.disconnect()
        logger.info("Cache disconnected")
        
        logger.info("Application shutdown complete")
    
    return stop_app
