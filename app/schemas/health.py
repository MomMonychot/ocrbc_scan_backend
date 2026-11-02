"""Health Check Schema Definitions.

Strict snake_case rules applied to all fields and models.
"""

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Structured response model for service health check verification."""

    status: str = Field(
        default="healthy",
        description="Overall service operational health state",
        examples=["healthy"],
    )
    app_name: str = Field(
        ...,
        description="Name of the backend service",
        examples=["District Administration OCR & Verification Platform"],
    )
    app_version: str = Field(
        ...,
        description="Current running release version",
        examples=["1.0.0"],
    )
    environment: str = Field(
        ...,
        description="Operating deployment environment",
        examples=["development", "production"],
    )
    timestamp_utc: str = Field(
        ...,
        description="Current server UTC timestamp",
    )
    zero_data_retention_enforced: bool = Field(
        default=True,
        description="Indicator showing whether Zero-Data-Retention security controls are active",
    )
    uptime_seconds: float = Field(
        ...,
        description="Service uptime in seconds since boot",
    )
