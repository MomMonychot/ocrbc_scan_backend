"""Template Box Styling and Typography Engine API Endpoints.

Architectural and Security Rationale:
- Exposes endpoints to customize extracted document text box styles, change typography,
  switch between official Cambodian civil registry fonts (Khmer OS Battambang, Siemreap,
  Muol Light, Bokor, Kantumruy Pro), toggle bold/weights, alter font sizes, and reposition coordinates.
- Generates render-ready CSS stylesheets and SVG graphics for immediate browser rendering or printing.
- Zero Data Retention: Layout configurations and field mappings exist only in-memory.
- Strict snake_case naming throughout.
"""

import logging
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status

from app.schemas.box_styling import (
    ApplyTemplateStylingRequest,
    ApplyTemplateStylingResponse,
    BoxStyleConfig,
    SupportedFontDetail,
)
from app.services.template_styler_service import template_styler_service

logger = logging.getLogger("district_templates_endpoint")

templates_router = APIRouter(
    prefix="/templates",
    tags=["template_box_styling"],
)


@templates_router.get(
    "/fonts",
    response_model=List[SupportedFontDetail],
    status_code=status.HTTP_200_OK,
    summary="List Supported Khmer Civil Fonts",
    description="Returns all official Cambodian typography fonts supported for template box styling.",
)
async def list_supported_khmer_fonts() -> List[SupportedFontDetail]:
    """Retrieves list of supported fonts with sample texts and recommended usages."""
    return template_styler_service.get_supported_fonts()


@templates_router.get(
    "/presets/{template_name}",
    response_model=Dict[str, BoxStyleConfig],
    status_code=status.HTTP_200_OK,
    summary="Get Default Box Styles for Template Preset",
    description="Returns standard typography, size, weight, and position settings for a designated template.",
)
async def get_template_preset_styles(template_name: str) -> Dict[str, BoxStyleConfig]:
    """Returns baseline box styling configuration for a template."""
    return template_styler_service.get_default_template_styles(template_name)


@templates_router.post(
    "/box-styles/apply",
    response_model=ApplyTemplateStylingResponse,
    status_code=status.HTTP_200_OK,
    summary="Apply Custom Box Styling to Extracted Document Fields",
    description=(
        "Applies customized typography (font family, bold weight, size pt), colors, and "
        "bounding box positions to extracted document fields. Returns structured styled boxes, "
        "full CSS stylesheets, and an SVG preview."
    ),
)
async def apply_custom_box_styles(payload: ApplyTemplateStylingRequest) -> ApplyTemplateStylingResponse:
    """Applies custom box styles and typography to extracted fields."""
    try:
        return template_styler_service.apply_styles_to_document(payload)
    except Exception as err:
        logger.error("Failed to apply template styling: %s", str(err), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error compiling template box styles: {str(err)}",
        )
