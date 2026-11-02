"""Main Application Entry Point.

Architectural and Security Rationale:
- FastAPI enterprise application scaffolding designed for District Administration OCR and Verification.
- Configures CORS with strict origin validation to mitigate cross-origin abuse.
- Injects custom SecurityHeadersMiddleware to enforce browser defense-in-depth (HSTS, CSP, no-cache).
- Implements centralized exception handlers to prevent raw exception leakage or PII exposure in error payloads.
- Strict snake_case standard across all internal variables, functions, and endpoints.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_v1_router
from app.core.config import app_settings
from app.core.security_headers import SecurityHeadersMiddleware

# Configure structured logging for government audit compliance
logging.basicConfig(
    level=logging.INFO if not app_settings.debug_mode else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("district_ocr_app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and teardown lifecycles."""
    logger.info("Initializing %s (v%s)", app_settings.app_name, app_settings.app_version)
    logger.info("Zero-Data-Retention Policy Active: in-memory wiping = %s", app_settings.enforce_in_memory_wipe)
    logger.info("Configured Allowed Origins: %s", app_settings.allowed_origins)
    yield
    logger.info("Gracefully shutting down %s", app_settings.app_name)


# Initialize FastAPI application
app = FastAPI(
    title=app_settings.app_name,
    version=app_settings.app_version,
    description="Production-grade document processing and OCR verification service for district administration.",
    docs_url="/docs" if app_settings.debug_mode else None,
    redoc_url="/redoc" if app_settings.debug_mode else None,
    openapi_url="/openapi.json" if app_settings.debug_mode else None,
    lifespan=lifespan,
)

# 1. Security Headers Middleware (Outermost layer to protect all responses)
app.add_middleware(SecurityHeadersMiddleware)

# 2. CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
    max_age=600,
)


# ---------------------------------------------------------------------------
# Centralized Exception Handlers (Prevent Information Disclosure)
# ---------------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Handles standard HTTP exceptions with consistent, sanitized JSON responses."""
    logger.warning("HTTP error occurred on path %s: status=%d, detail=%s", request.url.path, exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "path": request.url.path,
        },
    )


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handles input validation errors without leaking sensitive stack traces or internal models."""
    logger.warning("Validation error on path %s: %s", request.url.path, exc.errors())
    sanitized_errors = []
    for error in exc.errors():
        sanitized_errors.append(
            {
                "field": ".".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", "Invalid input value"),
                "type": error.get("type", "value_error"),
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "fail",
            "error_code": "VALIDATION_ERROR",
            "message": "Input validation failed for the submitted payload.",
            "details": sanitized_errors,
            "path": request.url.path,
        },
    )


@app.exception_handler(Exception)
async def custom_generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catches unhandled internal server errors and sanitizes output to safeguard server internals."""
    logger.error("Unhandled internal error encountered on path %s: %s", request.url.path, str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred while processing your request. Please contact technical support.",
            "path": request.url.path,
        },
    )


# ---------------------------------------------------------------------------
# Master API Routers
# ---------------------------------------------------------------------------
app.include_router(
    api_v1_router,
    prefix=app_settings.api_prefix,
)


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Root Service Verification",
    tags=["system_monitoring"],
)
async def root_ping() -> dict[str, str]:
    """Root endpoint for basic liveness and system identity checks."""
    return {
        "service": app_settings.app_name,
        "version": app_settings.app_version,
        "status": "operational",
        "api_documentation": f"{app_settings.api_prefix}/health_check",
    }


if __name__ == "__main__":
    import sys
    from pathlib import Path
    import uvicorn

    project_root = str(Path(__file__).resolve().parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    uvicorn.run(
        "app.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=True,
    )

