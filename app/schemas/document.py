"""Document Inspection and Verification Schema Definitions.

Architectural and Security Rationale:
- Strongly typed Pydantic v2 models enforcing strict validation on all incoming payloads
  and outbound responses.
- All field names adhere to the project-wide snake_case convention.
- Sanitized models prevent internal schema leaking or unvalidated input execution.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentInspectResponse(BaseModel):
    """Structured response model for pre-flight document quality gate evaluation."""

    is_accepted: bool = Field(
        ...,
        description="Indicates whether the document passes the minimum quality threshold (40%)",
        examples=[True],
    )
    confidence_score: float = Field(
        ...,
        description="Composite quality confidence score percentage (0.0 to 100.0)",
        examples=[87.5],
    )
    sharpness_score: float = Field(
        ...,
        description="Laplacian variance normalized sharpness score (0.0 to 100.0)",
        examples=[92.0],
    )
    laplacian_variance: float = Field(
        ...,
        description="Raw variance of the Laplacian edge detector",
        examples=[315.4],
    )
    brightness_score: float = Field(
        ...,
        description="Exposure and brightness balance score (0.0 to 100.0)",
        examples=[80.7],
    )
    mean_brightness: float = Field(
        ...,
        description="Grayscale mean pixel intensity value (0 to 255)",
        examples=[142.3],
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Rejection notice message if document fails the quality threshold",
        examples=["This file has quality issues (blur, dark, or incomplete). Please retake the photo."],
    )
    task_id: Optional[str] = Field(
        default=None,
        description="Celery asynchronous background task ID if accepted and dispatched",
        examples=["2f83c162-4b2a-4df4-a55e-18beff14187e"],
    )
    document_hash: str = Field(
        ...,
        description="Cryptographic SHA-256 fingerprint of the in-memory document for verification",
        examples=["e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"],
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Diagnostic metadata covering aspect ratio, blur detection, and luminance limits",
    )


class DocumentVerificationRequest(BaseModel):
    """Request payload containing OCR-extracted fields for municipal cross-referencing."""

    extracted_fields: Dict[str, Any] = Field(
        ...,
        description="Dictionary of extracted OCR fields (e.g. national_id, certificate_no, full_name_km, full_name_en)",
        examples=[
            {
                "national_id": "1204009821",
                "certificate_no": "BC-2024-009821",
                "full_name_km": "សុខ ចាន់ដារា",
                "full_name_en": "SOK CHANDARAA",
                "district_office": "ដូនពេញ (Daun Penh)",
            }
        ],
    )


class DiscrepancyField(BaseModel):
    """Detailed record of a field discrepancy detected during cross-referencing."""

    field: str = Field(..., description="Name of the evaluated field", examples=["full_name_en"])
    extracted_value: Optional[str] = Field(..., description="Raw text extracted by OCR", examples=["SOK CHANDARAA"])
    reference_value: Optional[str] = Field(..., description="Official text from reference record", examples=["SOK CHANDARA"])
    similarity_score: float = Field(..., description="Fuzzy match percentage score (0 to 100)", examples=[92.3])
    reason: Optional[str] = Field(default=None, description="Explanation of variance")


class DocumentVerificationResponse(BaseModel):
    """Structured response model for municipal record cross-referencing."""

    matched_records: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Authoritative municipal registry records matching the identity criteria",
    )
    confidence_level: float = Field(
        ...,
        description="Composite fuzzy verification confidence percentage (0.0 to 100.0)",
        examples=[96.0],
    )
    requires_manual_review: bool = Field(
        ...,
        description="Flag indicating if discrepancies or confidence below threshold mandate human officer review",
        examples=[False],
    )
    discrepancy_fields: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of fields where extracted text deviated from official reference records",
    )
    verified_fields: Dict[str, Any] = Field(
        ...,
        description="Final field dictionary with auto-corrections applied for minor OCR misreadings",
    )
    audit_hash: str = Field(
        ...,
        description="Ephemeral SHA-256 fingerprint of the verification transaction for audit trail",
    )
