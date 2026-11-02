"""Routers package initialization."""

from app.routers.document_router import document_router
from app.routers.verification_router import verification_router

__all__ = [
    "document_router",
    "verification_router",
]
