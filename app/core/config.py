"""Application Configuration Module.

Architectural and Security Rationale:
- Uses Pydantic BaseSettings for strongly-typed, environment-driven configuration.
- Follows 12-factor application design principles.
- Strict snake_case naming conventions for all settings and internal variables.
- Embeds Zero Data Retention (ZDR) configuration defaults so processing pipelines
  do not accidentally persist citizen civil registration documents to persistent disks.
"""

from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Core settings and environment variables for the document processing system."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General application identifiers
    app_name: str = Field(
        default="District Administration OCR & Verification Platform",
        description="Public identification title of the administrative system",
    )
    app_env: str = Field(
        default="development",
        description="Deployment stage (development, staging, production)",
    )
    app_version: str = Field(
        default="1.0.0",
        description="Semantic version of the backend service",
    )
    host: str = Field(
        default="127.0.0.1",
        description="Host binding address for the backend service",
    )
    port: int = Field(
        default=8003,
        description="Port for running the backend service",
    )
    debug_mode: bool = Field(
        default=False,
        description="Enable/disable verbose debug output and stack traces",
    )
    api_prefix: str = Field(
        default="/api/v1",
        description="Base routing prefix for API endpoints",
    )

    # Security: CORS and network boundaries
    allowed_origins: Union[List[str], str] = Field(
        default=[
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ],
        description="Authorized frontend domain origins permitted to access APIs",
    )
    secret_key: str = Field(
        default="insecure_default_secret_key_change_in_production_environment",
        description="Cryptographic signing key for session tokens and signatures",
    )

    # Security: Zero-Data-Retention (ZDR) baseline parameters
    max_file_size_mb: int = Field(
        default=15,
        description="Upper boundary for document payload size in megabytes",
    )
    ephemeral_ttl_seconds: int = Field(
        default=300,
        description="Strict TTL in seconds after which temporary memory cache is evicted",
    )
    enforce_in_memory_wipe: bool = Field(
        default=True,
        description="Enforce memory zeroization buffers after OCR processing terminates",
    )

    # Background Pipeline: Celery & Redis
    redis_url: str = Field(
        default="redis://127.0.0.1:6379/0",
        description="Redis broker and result backend URL for Celery async tasks",
    )
    celery_task_default_queue: str = Field(
        default="district_ocr_tasks",
        description="Default Celery queue for document processing workloads",
    )

    # Reference Database: Read-Only PostgreSQL Connection
    database_url_read_only: str = Field(
        default="postgresql+asyncpg://readonly_user:readonly_secure_password@127.0.0.1:5432/municipal_reference_db",
        description="Read-only PostgreSQL connection string for citizen record cross-referencing",
    )

    # Pre-Flight Quality Gate & Fuzzy Matching Thresholds
    quality_gate_min_score: float = Field(
        default=40.0,
        description="Minimum pre-flight quality confidence score threshold percentage (0-100)",
    )
    fuzzy_match_auto_correct_threshold: float = Field(
        default=85.0,
        description="Fuzzy matching threshold percentage above which minor OCR misreads are auto-corrected",
    )
    fuzzy_match_manual_review_threshold: float = Field(
        default=70.0,
        description="Fuzzy matching threshold percentage below which manual review is mandated",
    )

    # Multimodal Vision OCR for Handwritten Khmer
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API key for multimodal handwritten Khmer vision processing",
    )
    ocr_model_name: str = Field(
        default="gemini-2.5-flash",
        description="Primary multimodal vision model for cursive and handwritten Khmer documents",
    )
    ocr_fallback_model_name: str = Field(
        default="gemini-2.0-flash",
        description="Fallback vision model for handwritten Khmer document OCR",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        """Convert comma-separated string from .env into a list of strings."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


# Singleton instance accessible across the application lifecycle
app_settings = AppSettings()
