"""Document Quality Gate and Verification Endpoints.

Architectural and Security Rationale:
- Enforces front-line verification before any heavy OCR or background pipeline computation.
- Implements strict Zero-Data-Retention (ZDR): file streams are read entirely into memory
  buffers, evaluated, and zeroized upon completion. No files are written to disk.
- Applies the Pre-Flight Quality Gate (Laplacian sharpness + exposure variance).
- Cross-references OCR-extracted fields against authoritative municipal records and
  Cambodia administrative hierarchy using read-only sessions and RapidFuzz.
- All request parameters, function names, and JSON fields follow strict snake_case conventions.
"""

import hashlib
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import process_document_task
from app.core.config import app_settings
from app.core.zero_retention import EphemeralDocumentBuffer
from app.database.read_only_session import get_read_only_db
from app.schemas.document import (
    DocumentInspectResponse,
    DocumentVerificationRequest,
    DocumentVerificationResponse,
)
from app.services.quality_gate import evaluate_document_quality
from app.services.verification_service import cross_reference_extracted_text

logger = logging.getLogger("district_documents_endpoint")

documents_router = APIRouter(
    prefix="/documents",
    tags=["documents_and_verification"],
)


@documents_router.post(
    "/inspect",
    response_model=DocumentInspectResponse,
    status_code=status.HTTP_200_OK,
    summary="Pre-Flight Quality Gate Inspection",
    description=(
        "Evaluates document sharpness and exposure in volatile RAM. If quality exceeds 40%, "
        "dispatches an asynchronous background processing task."
    ),
)
async def inspect_document_quality(
    file: UploadFile = File(..., description="Document image file to inspect (JPEG, PNG, WebP)"),
) -> DocumentInspectResponse:
    """Pre-flight quality gate inspection endpoint."""
    logger.info("Received document inspection request: filename=%s", file.filename)

    file_bytes = await file.read()
    file_size_bytes = len(file_bytes)

    max_bytes = app_settings.max_file_size_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum permitted size of {app_settings.max_file_size_mb} MB.",
        )

    if file_size_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )

    ephemeral_buffer = EphemeralDocumentBuffer(raw_bytes=file_bytes)
    document_hash = ephemeral_buffer.document_hash
    task_id: Optional[str] = None

    try:
        quality_result = evaluate_document_quality(file_bytes=ephemeral_buffer.read_bytes())

        if quality_result.get("is_accepted", False):
            document_metadata = {
                "document_hash": document_hash,
                "confidence_score": quality_result.get("confidence_score", 0.0),
                "filename": file.filename,
                "file_size_bytes": file_size_bytes,
            }

            try:
                celery_async_result = process_document_task.delay(document_metadata)
                task_id = celery_async_result.id
                logger.info(
                    "Document %s passed quality gate. Dispatched Celery task id=%s",
                    document_hash,
                    task_id,
                )
            except Exception as celery_err:
                logger.warning(
                    "Celery task dispatch bypassed (broker connection: %s).",
                    str(celery_err),
                )
                task_id = "local_sync_mode"

        return DocumentInspectResponse(
            is_accepted=quality_result["is_accepted"],
            confidence_score=quality_result["confidence_score"],
            sharpness_score=quality_result["sharpness_score"],
            laplacian_variance=quality_result["laplacian_variance"],
            brightness_score=quality_result["brightness_score"],
            mean_brightness=quality_result["mean_brightness"],
            error_message=quality_result.get("error_message"),
            task_id=task_id,
            document_hash=document_hash,
            details=quality_result.get("details", {}),
        )
    finally:
        ephemeral_buffer.zeroize()


@documents_router.post(
    "/verify",
    response_model=DocumentVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Cross-Reference OCR Text Against Municipal Records and Geography",
    description=(
        "Safely verifies extracted OCR text against the master reference database using "
        "a read-only transaction, RapidFuzz matching, and national geographic validation. "
        "Applies auto-correction for minor misreadings (>= 85%) and flags anomalies for manual review."
    ),
)
async def verify_extracted_document(
    payload: DocumentVerificationRequest,
    db_session: Optional[AsyncSession] = Depends(get_read_only_db),
) -> DocumentVerificationResponse:
    """Verifies OCR-extracted fields against authoritative records and geographic gazetteer."""
    extracted_fields = payload.extracted_fields
    if not extracted_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload must include non-empty 'extracted_fields' dictionary.",
        )

    try:
        verification_result = await cross_reference_extracted_text(
            extracted_fields=extracted_fields,
            db_session=db_session,
        )
        return DocumentVerificationResponse(**verification_result)
    except Exception as err:
        logger.error("Document verification error: %s", str(err), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error during document cross-referencing. Please retry.",
        )
