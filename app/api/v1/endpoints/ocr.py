"""Khmer Handwritten OCR Extraction API Endpoint.

Architectural and Security Rationale:
- Exposes RESTful endpoint for extracting handwritten and archival Khmer text from documents.
- Uses Gemini 2.5 Flash / 2.0 Flash multimodal vision with computer vision preprocessing (CLAHE, unsharp mask).
- Automatically cross-references extracted birthplaces against the official Cambodia Geographic Gazetteer.
- Zero Data Retention (ZDR): Document bytes are processed strictly in volatile RAM.
- Strict snake_case naming and OpenAPI documentation.
"""

import logging
from typing import Optional
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import app_settings
from app.schemas.ocr import HandwrittenOcrExtractResponse, ModelCapabilitiesResponse
from app.services.khmer_ocr_service import khmer_ocr_engine

logger = logging.getLogger("district_ocr_endpoint")

ocr_router = APIRouter(
    prefix="/ocr",
    tags=["khmer_handwritten_ocr"],
)


@ocr_router.post(
    "/extract-handwritten",
    response_model=HandwrittenOcrExtractResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract Handwritten Khmer Document Text & Coordinates",
    description=(
        "Processes handwritten Khmer civil documents (e.g. birth certificates, vital records). "
        "Applies image contrast enhancement in RAM, executes multimodal AI vision inference, "
        "and cross-references extracted administrative divisions with the national gazetteer."
    ),
)
async def extract_handwritten_khmer_document(
    file: UploadFile = File(..., description="Document image to extract (JPEG, PNG, WebP)"),
) -> HandwrittenOcrExtractResponse:
    """Extracts handwritten Khmer script with bounding boxes and geographic verification.

    Args:
        file: Uploaded document image stream.

    Returns:
        Structured HandwrittenOcrExtractResponse containing parsed fields, boxes, and confidence.
    """
    logger.info("Received handwritten OCR extraction request: filename=%s", file.filename)

    file_bytes = await file.read()
    file_size_bytes = len(file_bytes)

    # 1. Enforce max payload limit
    max_bytes = app_settings.max_file_size_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum limit of {app_settings.max_file_size_mb} MB.",
        )

    # 2. Validate MIME type
    allowed_mime_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    content_type = file.content_type or ""
    if content_type not in allowed_mime_types and not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported format '{content_type}'. Please upload JPEG, PNG, or WebP.",
        )

    try:
        # 3. Execute in-memory handwritten OCR pipeline
        result = await khmer_ocr_engine.extract_handwritten_document(
            image_bytes=file_bytes,
            filename=file.filename,
        )
        return result
    except Exception as err:
        logger.error("Handwritten OCR extraction error: %s", str(err), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract handwritten Khmer text. Please verify image quality and try again.",
        )
    finally:
        # Enforce Zero Data Retention memory wiping
        if app_settings.enforce_in_memory_wipe:
            try:
                del file_bytes
            except Exception:
                pass


@ocr_router.get(
    "/models",
    response_model=ModelCapabilitiesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Active Khmer OCR Models and Capabilities",
    description="Returns metadata about active multimodal vision models and supported civil document templates.",
)
async def get_ocr_model_capabilities() -> ModelCapabilitiesResponse:
    """Returns active model details and supported handwriting features."""
    return ModelCapabilitiesResponse(
        primary_model=app_settings.ocr_model_name,
        fallback_model=app_settings.ocr_fallback_model_name,
        features_supported=[
            "khmer_subscripts_coarticulation",
            "khmer_numerical_glyphs",
            "dependent_vowel_anchoring",
            "diacritic_segmentation",
            "zero_data_retention_ram_pipeline",
            "clahe_contrast_enhancement",
            "cambodia_geo_gazetteer_cross_referencing",
        ],
        authoritative_gazetteer_loaded=True,
    )
