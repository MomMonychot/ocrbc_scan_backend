"""Document Verification and Municipal Cross-Referencing Router.

Architectural and Security Rationale:
- Exposes the authoritative cross-referencing endpoint for comparing OCR-extracted text
  against official municipal civil registry databases.
- Injects `get_read_only_db` dependency to enforce an immutable, read-only database transaction.
- Applies RapidFuzz high-performance matching to auto-correct minor glyph variations
  (>= 85% threshold) or route to administrative officer review (< 85% threshold).
- Guarantees Zero Data Retention: citizen records and extracted fields are compared in RAM
  and never committed or retained after the response stream is closed.
- All routes, methods, and payload structures use strict snake_case conventions.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.read_only_session import get_read_only_db
from app.schemas.document import (
    DocumentVerificationRequest,
    DocumentVerificationResponse,
)
from app.services.verification_service import cross_reference_extracted_text

logger = logging.getLogger("district_ocr_verification_router")

verification_router = APIRouter(
    prefix="/documents",
    tags=["document_verification"],
)


@verification_router.post(
    "/verify",
    response_model=DocumentVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Cross-Reference OCR Text Against Municipal Records",
    description=(
        "Safely verifies extracted OCR text against the master reference database using "
        "a read-only transaction and RapidFuzz matching. Applies auto-correction for minor "
        "misreadings (>= 85%) and flags anomalies for manual review."
    ),
)
async def verify_extracted_document(
    payload: DocumentVerificationRequest,
    db_session: Optional[AsyncSession] = Depends(get_read_only_db),
) -> DocumentVerificationResponse:
    """Verifies OCR-extracted fields against authoritative municipal registry records.

    Args:
        payload: Input JSON payload containing extracted fields (e.g., national_id, names).
        db_session: Injected read-only SQLAlchemy AsyncSession.

    Returns:
        DocumentVerificationResponse with match results, confidence level, and review flags.
    """
    extracted_fields = payload.extracted_fields
    if not extracted_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The extracted_fields dictionary cannot be empty.",
        )

    logger.info("Initiating read-only verification for extracted document payload")

    try:
        verification_result = await cross_reference_extracted_text(
            extracted_fields=extracted_fields,
            db_session=db_session,
        )

        return DocumentVerificationResponse(
            matched_records=verification_result["matched_records"],
            confidence_level=verification_result["confidence_level"],
            requires_manual_review=verification_result["requires_manual_review"],
            discrepancy_fields=verification_result["discrepancy_fields"],
            verified_fields=verification_result["verified_fields"],
            audit_hash=verification_result["audit_hash"],
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unhandled error during document cross-reference verification: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while cross-referencing document against municipal records.",
        )
