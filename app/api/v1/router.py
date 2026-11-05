"""API v1 Master Router Module.

Architectural and Security Rationale:
- Aggregates all v1 enterprise endpoints under the standardized `/api/v1` namespace.
- Strictly adheres to snake_case naming conventions and OpenAPI specifications.
- Endpoints included:
  1. System Health Telemetry (/api/v1/health_check)
  2. Pre-Flight Quality Gate & Verification (/api/v1/documents/inspect, /api/v1/documents/verify)
  3. Multimodal Handwritten Khmer OCR Extraction (/api/v1/ocr/extract-handwritten, /api/v1/ocr/models)
  4. Cambodia National Geographic Gazetteer & Birthplace Resolution (/api/v1/geo/...)
  5. Template Box Styling & Khmer Civil Typography (/api/v1/templates/...)
"""

from fastapi import APIRouter

from app.api.v1.endpoints.documents import documents_router
from app.api.v1.endpoints.geo import geo_router
from app.api.v1.endpoints.health_check import health_check_router
from app.api.v1.endpoints.ocr import ocr_router
from app.api.v1.endpoints.templates import templates_router

api_v1_router = APIRouter()

# 1. System Health and Integrity Telemetry
api_v1_router.include_router(
    health_check_router,
    tags=["system_monitoring"],
)

# 2. Document Quality Gate and Verification
api_v1_router.include_router(
    documents_router,
    tags=["documents_and_verification"],
)

# 3. Multimodal Handwritten Khmer OCR Extraction
api_v1_router.include_router(
    ocr_router,
    tags=["khmer_handwritten_ocr"],
)

# 4. Cambodia Geographic Gazetteer and Birthplace Resolution
api_v1_router.include_router(
    geo_router,
    tags=["cambodia_geographic_verification"],
)

# 5. Template Box Styling and Khmer Civil Typography
api_v1_router.include_router(
    templates_router,
    tags=["template_box_styling"],
)
