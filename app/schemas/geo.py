"""Cambodia Geographic Administrative Verification Schemas.

Architectural and Security Rationale:
- Strongly-typed Pydantic v2 schemas for geographic validation endpoints.
- Validates extracted document text against the 25 Provinces/Capitals, Districts/Khans/Krongs,
  Communes/Sangkats, and Villages/Phums of Cambodia.
- Zero Data Retention: Inputs and outputs are processed in-memory and not stored.
- All field names strictly use snake_case.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ValidateBirthplaceRequest(BaseModel):
    """Payload for validating a handwritten or printed birthplace against the national gazetteer."""

    raw_birthplace_text: Optional[str] = Field(
        default=None,
        description="Full raw extracted birthplace text string",
        examples=["ភូមិព្រែកតាពៅ សង្កាត់ដើមមៀន ក្រុងតាខ្មៅ ខេត្តកណ្តាល"],
    )
    province: Optional[str] = Field(
        default=None,
        description="Explicit province or capital name if parsed individually",
        examples=["ខេត្តកណ្តាល"],
    )
    district: Optional[str] = Field(
        default=None,
        description="Explicit district/khan/krong name if parsed individually",
        examples=["ក្រុងតាខ្មៅ"],
    )
    commune: Optional[str] = Field(
        default=None,
        description="Explicit commune or sangkat name if parsed individually",
        examples=["សង្កាត់ដើមមៀន"],
    )
    village: Optional[str] = Field(
        default=None,
        description="Explicit village or phum name if parsed individually",
        examples=["ភូមិព្រែកតាពៅ"],
    )


class GeoEntityDetail(BaseModel):
    """Standardized representation of a single administrative division."""

    code: Optional[str] = Field(default=None, description="Official NIS/Ministry code", examples=["0811"])
    name_km: Optional[str] = Field(default=None, description="Official Khmer name", examples=["ក្រុងតាខ្មៅ"])
    name_en: Optional[str] = Field(default=None, description="Official Latin transliteration", examples=["Krong Ta Khmau"])
    score: float = Field(default=0.0, description="Fuzzy match confidence score (0.0 to 100.0)", examples=[98.2])


class ValidateBirthplaceResponse(BaseModel):
    """Structured response detailing the verification of an administrative address."""

    is_valid_administrative_path: bool = Field(
        ...,
        description="Whether the administrative hierarchy (Province -> District -> Commune) is legitimate",
        examples=[True],
    )
    confidence_score: float = Field(
        ...,
        description="Composite matching confidence percentage across all divisions (0.0 to 100.0)",
        examples=[97.4],
    )
    province: Optional[GeoEntityDetail] = Field(default=None)
    district: Optional[GeoEntityDetail] = Field(default=None)
    commune: Optional[GeoEntityDetail] = Field(default=None)
    village: Optional[GeoEntityDetail] = Field(default=None)
    standardized_address_km: str = Field(
        ...,
        description="Official standardized address in Khmer script",
        examples=["ភូមិព្រែកតាពៅ សង្កាត់ដើមមៀន ក្រុងតាខ្មៅ ខេត្តកណ្តាល"],
    )
    standardized_address_en: str = Field(
        ...,
        description="Official standardized address in Latin script",
        examples=["Phum Prek Ta Pov, Sangkat Daeum Mien, Krong Ta Khmau, Kandal Province"],
    )
    auto_corrected: bool = Field(
        ...,
        description="True if OCR spelling deviations were successfully corrected to match official gazetteer",
        examples=[True],
    )
    discrepancy_alerts: List[str] = Field(
        default_factory=list,
        description="Diagnostic warnings regarding unmatched or conflicting administrative levels",
    )


class ProvinceSummary(BaseModel):
    """Summary of a Cambodian Province or Capital for dropdown selections."""

    code: str = Field(..., examples=["12"])
    name_km: str = Field(..., examples=["រាជធានីភ្នំពេញ"])
    name_en: str = Field(..., examples=["Phnom Penh Capital"])
    type: str = Field(..., examples=["Capital"])
    district_count: int = Field(..., examples=[14])
