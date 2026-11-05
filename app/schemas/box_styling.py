"""Template Bounding-Box Styling and Typography Schemas.

Architectural and Security Rationale:
- Powers dynamic styling of document extracted text blocks into new municipal certificate templates.
- Enforces strict validation on font family names, sizes, weights, and positioning coordinates.
- Supports official civil registry fonts:
  * Khmer OS Battambang (Standard administrative body)
  * Khmer OS Siemreap (Modern clean sans)
  * Khmer OS Muol Light (Official heading, Kingdom header, national motto)
  * Khmer OS Bokor (Traditional formal banner)
  * Kantumruy Pro (Modern government digital standard)
  * Khmer OS Fasthand (Signatory/cursive preview)
- Generates corresponding CSS and SVG templates for immediate frontend rendering or vector printing.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class KhmerFontFamily(str, Enum):
    """Authoritative typography fonts approved for Cambodian civil registration."""

    KHMER_OS_BATTAMBANG = "Khmer OS Battambang"
    KHMER_OS_SIEMREAP = "Khmer OS Siemreap"
    KHMER_OS_MOUL_LIGHT = "Khmer OS Muol Light"
    KHMER_OS_BOKOR = "Khmer OS Bokor"
    KANTUMRUY_PRO = "Kantumruy Pro"
    KHMER_OS_FASTHAND = "Khmer OS Fasthand"


class FontWeight(str, Enum):
    """Typography weight options."""

    NORMAL = "normal"
    MEDIUM = "500"
    SEMIBOLD = "600"
    BOLD = "bold"


class TextAlign(str, Enum):
    """Text alignment alignment options."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


class BoxStyleConfig(BaseModel):
    """Styling and geometry rules for an individual extracted text block."""

    font_family: KhmerFontFamily = Field(
        default=KhmerFontFamily.KHMER_OS_BATTAMBANG,
        description="Font family to apply to the text box",
        examples=[KhmerFontFamily.KHMER_OS_BATTAMBANG],
    )
    font_size_pt: float = Field(
        default=12.0,
        ge=6.0,
        le=72.0,
        description="Font size in points (pt)",
        examples=[13.5],
    )
    font_weight: FontWeight = Field(
        default=FontWeight.NORMAL,
        description="Font weight (normal, medium, semibold, bold)",
        examples=[FontWeight.BOLD],
    )
    font_style: str = Field(
        default="normal",
        description="Font style (normal or italic)",
        examples=["normal"],
    )
    text_color: str = Field(
        default="#0F172A",
        description="Hexadecimal text color",
        examples=["#0F172A"],
    )
    text_align: TextAlign = Field(
        default=TextAlign.LEFT,
        description="Horizontal text alignment",
        examples=[TextAlign.LEFT],
    )
    line_height: float = Field(
        default=1.5,
        ge=1.0,
        le=3.0,
        description="Line height multiplier",
        examples=[1.5],
    )
    letter_spacing_px: float = Field(
        default=0.0,
        ge=-2.0,
        le=10.0,
        description="Letter spacing in pixels",
        examples=[0.0],
    )
    background_color: str = Field(
        default="transparent",
        description="CSS background color for the text box",
        examples=["transparent"],
    )
    border_color: str = Field(
        default="#CBD5E1",
        description="Hexadecimal border color",
        examples=["#CBD5E1"],
    )
    border_width_px: float = Field(
        default=1.0,
        ge=0.0,
        le=10.0,
        description="Border width in pixels (0 for borderless print output)",
        examples=[1.0],
    )
    border_radius_px: float = Field(
        default=8.0,
        ge=0.0,
        le=32.0,
        description="Border corner radius in pixels",
        examples=[8.0],
    )
    padding_px: int = Field(
        default=6,
        ge=0,
        le=48,
        description="Internal box padding in pixels",
        examples=[6],
    )
    box_x_pct: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Horizontal position percentage (0.0 to 100.0)",
        examples=[10.0],
    )
    box_y_pct: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Vertical position percentage (0.0 to 100.0)",
        examples=[25.0],
    )
    box_width_pct: float = Field(
        ...,
        ge=1.0,
        le=100.0,
        description="Width percentage (1.0 to 100.0)",
        examples=[35.0],
    )
    box_height_pct: float = Field(
        ...,
        ge=1.0,
        le=100.0,
        description="Height percentage (1.0 to 100.0)",
        examples=[6.0],
    )
    z_index: int = Field(
        default=1,
        ge=0,
        le=100,
        description="Stacking layer order",
        examples=[1],
    )


class ApplyTemplateStylingRequest(BaseModel):
    """Request payload to apply custom box styles to extracted document fields."""

    template_name: str = Field(
        default="standard_birth_certificate_v1",
        description="Base template profile to style against",
        examples=["standard_birth_certificate_v1"],
    )
    field_styles: Dict[str, BoxStyleConfig] = Field(
        ...,
        description="Dictionary mapping field keys to individual box style configurations",
    )
    document_fields: Dict[str, Any] = Field(
        ...,
        description="Dictionary of field values extracted from OCR or verified database",
        examples=[
            {
                "national_id": "1204009821",
                "certificate_no": "BC-2024-009821",
                "full_name_km": "សុខ ចាន់ដារា",
                "full_name_en": "SOK CHANDARA",
                "birth_place": "ភូមិព្រែកតាពៅ សង្កាត់ដើមមៀន ក្រុងតាខ្មៅ ខេត្តកណ្តាល",
            }
        ],
    )


class StyledBoxOutput(BaseModel):
    """Render-ready styled text box definition."""

    field_key: str
    value: str
    css_style_inline: str
    css_classes: str
    computed_geometry: Dict[str, float]
    svg_element: str


class ApplyTemplateStylingResponse(BaseModel):
    """Structured response containing styled boxes, CSS stylesheet, and SVG template."""

    template_name: str
    styled_boxes: Dict[str, StyledBoxOutput]
    full_css_stylesheet: str
    svg_preview: str


class SupportedFontDetail(BaseModel):
    """Metadata describing a supported Khmer typography font."""

    identifier: str
    name: str
    khmer_sample_text: str
    recommended_use: str
    is_heading_font: bool
    google_fonts_family_name: Optional[str] = None
