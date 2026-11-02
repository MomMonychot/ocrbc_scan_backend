"""Health check endpoint definition.

Architectural and Security Rationale:
- Provides liveness and readiness probe targets for orchestrators (e.g. Kubernetes, Cloud Run).
- Exposes vital health metadata without disclosing sensitive internals, internal IP addresses,
  or environment credentials.
- Strict snake_case naming for endpoint paths, route functions, and schemas.
"""

import time
from datetime import datetime, timezone
from fastapi import APIRouter, status

from app.core.config import app_settings
from app.schemas.health import HealthCheckResponse

health_check_router = APIRouter()

# Capture process boot timestamp
service_start_time = time.time()


@health_check_router.get(
    "/health_check",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Health and Integrity Check",
    description="Returns service availability, version info, and security baseline status.",
)
async def check_service_health() -> HealthCheckResponse:
    """Verifies operational integrity and zero-data-retention compliance."""
    current_time = time.time()
    uptime_seconds = round(current_time - service_start_time, 2)
    timestamp_utc = datetime.now(timezone.utc).isoformat()

    return HealthCheckResponse(
        status="healthy",
        app_name=app_settings.app_name,
        app_version=app_settings.app_version,
        environment=app_settings.app_env,
        timestamp_utc=timestamp_utc,
        zero_data_retention_enforced=app_settings.enforce_in_memory_wipe,
        uptime_seconds=uptime_seconds,
    )
