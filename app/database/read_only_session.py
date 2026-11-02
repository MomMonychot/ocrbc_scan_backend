"""Read-Only Database Connection and Session Lifecycle.

Architectural and Security Rationale:
- In civil registration verification, municipal reference databases contain master identity records.
- This module creates an isolated, strictly read-only SQLAlchemy asynchronous engine.
- Defensive enforcement:
  1. Driver-level read-only server parameter (`default_transaction_read_only=on` for PostgreSQL/asyncpg).
  2. Engine-level execution options (`{"postgresql_readonly": True}`).
  3. Session-level read-only transaction initialization (`SET TRANSACTION READ ONLY`).
  4. Explicit rollback on session teardown to prevent any lingering state.
  5. Resilient connection handling: If the physical database is undergoing maintenance or
     unreachable, yields None with structured logging so fallback verification handles the request.
- Strictly adheres to the Zero Data Retention policy: no citizen queries or extracted OCR texts
  are stored, cached persistently, or audited beyond in-memory execution traces.
- All function and variable names use strict snake_case.
"""

import logging
from typing import AsyncGenerator, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import app_settings

logger = logging.getLogger("district_ocr_read_only_db")


def build_read_only_engine(database_url: str) -> AsyncEngine:
    """Creates a hardened SQLAlchemy async engine configured for read-only access.

    Args:
        database_url: SQLAlchemy async database URL (e.g., postgresql+asyncpg://...)

    Returns:
        Configured AsyncEngine with connection pool and read-only flags.
    """
    connect_args = {}
    if "postgresql" in database_url:
        # Enforce read-only transaction setting at the asyncpg driver level
        connect_args["server_settings"] = {
            "default_transaction_read_only": "on",
        }

    return create_async_engine(
        database_url,
        echo=app_settings.debug_mode,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
        connect_args=connect_args,
        execution_options={"postgresql_readonly": True},
    )


# Master read-only engine singleton
read_only_engine: AsyncEngine = build_read_only_engine(app_settings.database_url_read_only)

# Thread-safe async session factory
AsyncReadOnlySessionLocal = async_sessionmaker(
    bind=read_only_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_read_only_db() -> AsyncGenerator[Optional[AsyncSession], None]:
    """FastAPI dependency yielding a strictly read-only asynchronous database session.

    Enforcement:
    - Sets transaction isolation to READ ONLY.
    - If any code attempts an INSERT, UPDATE, or DELETE, the database aborts the query immediately.
    - Ensures automatic rollback upon completion.
    - Gracefully degrades to None if the remote host/role is unavailable, allowing offline fallback.

    Yields:
        Optional[AsyncSession]: Active read-only session for municipal record lookups, or None if offline.
    """
    try:
        async with AsyncReadOnlySessionLocal() as session:
            try:
                # Enforce read-only transaction state on the active session
                await session.execute(text("SET TRANSACTION READ ONLY;"))
                yield session
            except Exception as query_exc:
                logger.error("Error during read-only transaction execution: %s", query_exc)
                await session.rollback()
                raise
            finally:
                await session.rollback()
    except Exception as conn_exc:
        logger.warning(
            "Read-only reference database unreachable or role unconfigured (%s). Using fallback evaluation.",
            conn_exc,
        )
        yield None
