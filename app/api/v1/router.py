"""API v1 master router module.

Consolidates all v1 sub-routers following strict snake_case conventions.
"""

from fastapi import APIRouter
from app.api.v1.endpoints.health_check import health_check_router
from app.routers.document_router import document_router
from app.routers.verification_router import verification_router

api_v1_router = APIRouter()

# 1. System Health and Integrity Telemetry
api_v1_router.include_router(
    health_check_router,
    tags=["system_monitoring"],
)

# 2. Document Quality Gate and Inspection
api_v1_router.include_router(
    document_router,
    tags=["document_inspection"],
)

# 3. Document Verification and Municipal Cross-Referencing
api_v1_router.include_router(
    verification_router,
    tags=["document_verification"],
)
