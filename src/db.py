"""
Database configuration and session management.

Phase II: SQLModel engine initialization for PostgreSQL.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Generator

import structlog
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from src.config import settings

logger = structlog.get_logger()


@lru_cache
def get_engine() -> Engine:
    """
    Create and cache database engine.

    Uses DATABASE_URL from environment configuration.
    
    Returns:
        SQLAlchemy Engine instance.
    """
    # For PostgreSQL, we need to handle the connection properly
    connect_args = {}
    
    # Create engine with appropriate settings
    engine = create_engine(
        settings.database_url,
        echo=settings.environment == "development",
        pool_pre_ping=True,  # Verify connections before use
        connect_args=connect_args,
    )
    
    logger.info(
        "database_engine_created",
        database_url=settings.database_url.split("@")[0] + "@***",  # Hide password
    )
    
    return engine


def create_tables() -> None:
    """
    Create all database tables.

    Should be called on application startup.
    """
    engine = get_engine()
    
    # Import models to ensure they're registered with SQLModel
    from src.models.tasks import TaskDB  # noqa: F401
    from src.models.user import UserDB  # noqa: F401
    
    SQLModel.metadata.create_all(engine)
    logger.info("database_tables_created")


def get_session() -> Generator[Session, None, None]:
    """
    Get database session as dependency.

    Yields:
        SQLModel Session for database operations.
    """
    engine = get_engine()
    with Session(engine) as session:
        yield session


def drop_tables() -> None:
    """
    Drop all database tables.

    WARNING: This will delete all data. Use only for testing.
    """
    engine = get_engine()
    SQLModel.metadata.drop_all(engine)
    logger.warning("database_tables_dropped")
