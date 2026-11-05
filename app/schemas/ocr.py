"""Khmer Handwritten OCR Extraction Schema Definitions.

Architectural and Security Rationale:
- Formulates strongly-typed Pydantic v2 schemas for document OCR extraction.
- Accommodates handwriting confidence metrics, multi-script bounding boxes, and
  integration with the Cambodia Geographic Gazetteer.
- Strictly adheres to snake_case naming conventions.
- Zero Data Retention: Extraction outputs are returned strictly in the HTTP response
  stream and never stored in persistent databases.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Normalized relative bounding coordinates (0.0% to 100.0%) for rendering on canvas."""

    x_pct: float = Field(
        ...,
        description="Left offset percentage from document left edge (0.0 to 100.0)",
        examples=[12.5],
    )
    y_pct: float = Field(
        ...,
        description="Top offset percentage from document top edge (0.0 to 100.0)",
        examples=[34.2],
    )
    width_pct: float = Field(
        ...,
        description="Width percentage relative to total document width (0.0 to 100.0)",
        examples=[45.0],
    )
    height_pct: float = Field(
        ...,
        description="Height percentage relative to total document height (0.0 to 100.0)",
        examples=[5.8],
    )


class ExtractedFieldDetail(BaseModel):
    """Granular field extracted by the multimodal Khmer AI model."""

    field_key: str = Field(
        ...,
        description="Standardized machine identifier (e.g. citizen_name_km, certificate_no)",
        examples=["citizen_name_km"],
    )
    label_km: str = Field(
        ...,
        description="Official Khmer label name",
        examples=["ឈ្មោះសាមីខ្លួន (ខ្មែរ)"],
    )
    label_en: str = Field(
        ...,
        description="Standard Latin label name",
        examples=["Full Name (Khmer)"],
    )
    raw_text: str = Field(
        ...,
        description="Raw text recognized directly from the image",
        examples=["សុខ ចាន់ដារា"],
    )
    normalized_text: str = Field(
        ...,
        description="Normalized Unicode text with zero-width spaces cleaned and standard diacritics",
        examples=["សុខ ចាន់ដារា"],
    )
    confidence_score: float = Field(
        ...,
        description="AI confidence percentage score (0.0 to 100.0)",
        examples=[96.5],
    )
    is_handwritten: bool = Field(
        default=True,
        description="Indicates whether the field was detected as handwriting vs pre-printed form text",
    )
    bounding_box: Optional[BoundingBox] = Field(
        default=None,
        description="Coordinates for highlighting or template box repositioning",
    )


class HandwrittenOcrExtractResponse(BaseModel):
    """Top-level structured response for Khmer handwritten OCR extraction."""

    status: str = Field(
        default="success",
        description="Execution status indicator",
        examples=["success"],
    )
    document_type: str = Field(
        ...,
        description="Detected document template classification",
        examples=["birth_certificate_standard"],
    )
    model_used: str = Field(
        ...,
        description="Identifier of the vision AI model executed",
        examples=["gemini-2.5-flash"],
    )
    processing_duration_ms: float = Field(
        ...,
        description="Round-trip OCR inference latency in milliseconds",
        examples=[682.4],
    )
    extracted_fields: Dict[str, ExtractedFieldDetail] = Field(
        ...,
        description="Map of field keys to detailed extracted field entities",
    )
    raw_full_text: str = Field(
        ...,
        description="Complete unsegmented OCR transcript of the document",
    )
    preprocessing_applied: List[str] = Field(
        default_factory=list,
        description="List of computer vision image enhancements executed prior to inference",
        examples=[["clahe_contrast_enhancement", "laplacian_unsharp_mask", "deskew_normalization"]],
    )
    geographic_verification: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Automated cross-reference report against the Cambodia National Geographic Gazetteer",
    )
    audit_hash: str = Field(
        ...,
        description="Ephemeral SHA-256 fingerprint for verification traceability without PII retention",
    )


class ModelCapabilitiesResponse(BaseModel):
    """System information on supported AI vision models for handwritten Khmer processing."""

    primary_model: str = Field(..., examples=["gemini-2.5-flash"])
    fallback_model: str = Field(..., examples=["gemini-2.0-flash"])
    features_supported: List[str] = Field(..., examples=[["khmer_subscripts", "cursive_ink_parsing", "zdr_ram_buffers"]])
    authoritative_gazetteer_loaded: bool = Field(default=True)
    supported_document_types: List[str] = Field(
        default_factory=lambda: [
            "birth_certificate_standard",
            "birth_certificate_certified_copy",
            "national_id_card",
            "residence_book",
        ]
    )
