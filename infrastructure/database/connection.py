"""
Database connection manager with async support and connection pooling
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import settings


class AsyncDatabaseManager:
    """Manages async database connections with pooling"""
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self):
        """Initialize database engine"""
        if self._engine is None:
            # Use SQLite for development if no PostgreSQL URL
            if settings.is_development and not settings.DATABASE_URL:
                database_url = settings.SQLITE_URL or "sqlite+aiosqlite:///./wealthhive.db"
                self._engine = create_async_engine(
                    database_url,
                    echo=settings.DEBUG,
                    poolclass=NullPool,  # SQLite doesn't support pooling well
                )
            else:
                self._engine = create_async_engine(
                    str(settings.DATABASE_URL),
                    echo=settings.DEBUG,
                    pool_size=settings.DATABASE_POOL_SIZE,
                    max_overflow=settings.DATABASE_MAX_OVERFLOW,
                    pool_pre_ping=True,
                )
            
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup"""
        if self._session_factory is None:
            await self.initialize()
        
        session = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def close(self):
        """Close all connections"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_session() as session:
                await session.execute("SELECT 1")
                return True
        except Exception:
            return False


# Convenience function for dependency injection
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions"""
    manager = AsyncDatabaseManager()
    async with manager.get_session() as session:
        yield session
