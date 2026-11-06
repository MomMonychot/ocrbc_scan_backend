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


class GeoEntityCreate(BaseModel):
    """Payload to add a new administrative division."""

    level: str = Field(
        ...,
        description="Administrative tier: 'province', 'district', 'commune', or 'village'",
        examples=["village"],
    )
    code: str = Field(
        ...,
        description="Official NIS Administrative code (e.g. '08110203')",
        examples=["08110203"],
    )
    name_km: str = Field(
        ...,
        description="Official Khmer name",
        examples=["ភូមិព្រែកសំរោង"],
    )
    name_en: str = Field(
        ...,
        description="Official Latin transliteration",
        examples=["Phum Prek Samraong"],
    )
    type: Optional[str] = Field(
        default=None,
        description="Classification type (e.g. 'Province', 'Capital', 'Khan', 'Krong', 'Sangkat')",
        examples=["Phum"],
    )
    parent_code: Optional[str] = Field(
        default=None,
        description="Parent administrative division code (required for district, commune, and village)",
        examples=["081102"],
    )


class GeoEntityUpdate(BaseModel):
    """Payload to update an existing administrative division."""

    name_km: str = Field(
        ...,
        description="Updated Khmer name",
        examples=["ភូមិព្រែកសំរោងថ្មី"],
    )
    name_en: str = Field(
        ...,
        description="Updated Latin transliteration",
        examples=["Phum Prek Samraong Thmei"],
    )
    type: Optional[str] = Field(
        default=None,
        description="Classification type",
        examples=["Phum"],
    )


class PaginatedGeoEntitiesResponse(BaseModel):
    """Paginated tabular output of administrative divisions."""

    total: int = Field(..., description="Total matched entity count", examples=[25])
    page: int = Field(..., description="Current page number (1-indexed)", examples=[1])
    page_size: int = Field(..., description="Rows per page", examples=[15])
    total_pages: int = Field(..., description="Calculated total pages", examples=[2])
    items: List[Dict[str, Any]] = Field(..., description="List of entity records")


class GeoReportCreate(BaseModel):
    """Payload to submit a user report regarding an error in administrative divisions."""

    division_code: str = Field(..., description="NIS code of the division", examples=["14010101"])
    division_level: str = Field(..., description="Level: 'province', 'district', 'commune', or 'village'", examples=["village"])
    current_name_km: str = Field(..., description="Current displayed Khmer name", examples=["ភូមិតាកែវ"])
    current_name_en: Optional[str] = Field(default=None, description="Current displayed Latin transliteration", examples=["Ta Kaev"])
    issue_type: str = Field(
        ...,
        description="Type of error: 'spelling', 'incorrect_name', 'wrong_hierarchy', or 'other'",
        examples=["spelling"],
    )
    suggested_name_km: Optional[str] = Field(default=None, description="User suggested correct Khmer name", examples=["ភូមិតាកែវលើ"])
    suggested_name_en: Optional[str] = Field(default=None, description="User suggested Latin name", examples=["Ta Kaev Leu"])
    notes: Optional[str] = Field(default=None, description="Detailed explanation of the error", examples=["អក្ខរាវិរុទ្ធខ្វះស្រៈ"])
    reported_by: Optional[str] = Field(default="user", description="Username or citizen identifier", examples=["civil_officer_01"])


class GeoReportUpdate(BaseModel):
    """Payload for administrators to update the status of a reported issue."""

    status: str = Field(..., description="Updated status: 'pending', 'read', or 'resolved'", examples=["read"])
    admin_notes: Optional[str] = Field(default=None, description="Notes added by administrator during review")


class GeoReportItem(BaseModel):
    """Full detail of a submitted administrative division report."""

    id: str = Field(..., examples=["rep-20261106-001"])
    division_code: str = Field(..., examples=["14010101"])
    division_level: str = Field(..., examples=["village"])
    current_name_km: str = Field(..., examples=["ភូមិតាកែវ"])
    current_name_en: Optional[str] = Field(default=None, examples=["Ta Kaev"])
    parent_hierarchy_km: Optional[str] = Field(default=None, examples=["ខេត្តព្រៃវែង > ស្រុកបាភ្នំ > ឃុំបឹងព្រះ"])
    parent_hierarchy_en: Optional[str] = Field(default=None, examples=["Prey Veng > Ba Phnum > Boeng Preah"])
    issue_type: str = Field(..., examples=["spelling"])
    suggested_name_km: Optional[str] = Field(default=None, examples=["ភូមិតាកែវលើ"])
    suggested_name_en: Optional[str] = Field(default=None, examples=["Ta Kaev Leu"])
    notes: Optional[str] = Field(default=None)
    reported_by: str = Field(default="user")
    created_at: str = Field(..., examples=["2026-11-06T08:30:00+07:00"])
    status: str = Field(default="pending", description="'pending', 'read', or 'resolved'", examples=["pending"])
    admin_notes: Optional[str] = Field(default=None)


class GeoReportListResponse(BaseModel):
    """Response containing list of administrative reports and unread tally."""

    total: int = Field(..., examples=[2])
    unread_count: int = Field(..., examples=[1])
    reports: List[GeoReportItem]

