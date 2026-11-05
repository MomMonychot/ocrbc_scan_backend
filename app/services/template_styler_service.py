"""Template Bounding-Box Styling and Dynamic Typography Engine.

Architectural and Security Rationale:
- Enables administrative officers and template designers to alter typography, font family,
  font size, weight (bold/normal), alignment, and spatial coordinates for extracted document fields.
- Official civil registration typography support:
  * Khmer OS Battambang: Administrative standard body text
  * Khmer OS Siemreap: Clean sans-serif certificate body
  * Khmer OS Muol Light: Formal Kingdom title (ព្រះរាជាណាចក្រកម្ពុជា) & national motto
  * Khmer OS Bokor: Traditional ceremonial banners
  * Kantumruy Pro: Contemporary digital government portal standard
- Generates inline CSS, full stylesheets, and scalable vector SVG templates.
- Strict snake_case naming and zero data retention.
"""

import html
import logging
from typing import Any, Dict, List, Optional

from app.schemas.box_styling import (
    ApplyTemplateStylingRequest,
    ApplyTemplateStylingResponse,
    BoxStyleConfig,
    FontWeight,
    KhmerFontFamily,
    StyledBoxOutput,
    SupportedFontDetail,
    TextAlign,
)

logger = logging.getLogger("district_template_styler_service")


SUPPORTED_FONTS: List[SupportedFontDetail] = [
    SupportedFontDetail(
        identifier="khmer_os_battambang",
        name="Khmer OS Battambang",
        khmer_sample_text="ព្រះរាជាណាចក្រកម្ពុជា - សំបុត្រកំណើតផ្លូវការ",
        recommended_use="Standard administrative body text, citizen names, addresses, and dates.",
        is_heading_font=False,
        google_fonts_family_name="Battambang",
    ),
    SupportedFontDetail(
        identifier="khmer_os_siemreap",
        name="Khmer OS Siemreap",
        khmer_sample_text="រាជធានីភ្នំពេញ រដ្ឋបាលក្រុង ស្រុក ខណ្ឌ",
        recommended_use="Modern clean sans-serif for secondary labels, table headers, and Latin dual-script.",
        is_heading_font=False,
        google_fonts_family_name="Siemreap",
    ),
    SupportedFontDetail(
        identifier="khmer_os_moul_light",
        name="Khmer OS Muol Light",
        khmer_sample_text="ព្រះរាជាណាចក្រកម្ពុជា ជាតិ សាសនា ព្រះមហាក្សត្រ",
        recommended_use="Official Kingdom headers, National Motto, Certificate titles, and ministry seals.",
        is_heading_font=True,
        google_fonts_family_name="Moul",
    ),
    SupportedFontDetail(
        identifier="khmer_os_bokor",
        name="Khmer OS Bokor",
        khmer_sample_text="ព្រះរាជក្រឹត្យ និងបទបញ្ញត្តិរដ្ឋបាល",
        recommended_use="Traditional ceremonial banners, historical certificates, and decorative frames.",
        is_heading_font=True,
        google_fonts_family_name="Bokor",
    ),
    SupportedFontDetail(
        identifier="kantumruy_pro",
        name="Kantumruy Pro",
        khmer_sample_text="ប្រព័ន្ធផ្ទៀងផ្ទាត់ឯកសាររដ្ឋបាលឌីជីថល",
        recommended_use="Contemporary administrative digital screens and high-DPI modern print engines.",
        is_heading_font=False,
        google_fonts_family_name="Kantumruy+Pro",
    ),
    SupportedFontDetail(
        identifier="khmer_os_fasthand",
        name="Khmer OS Fasthand",
        khmer_sample_text="ហត្ថលេខា និងត្រារដ្ឋបាលឃុំសង្កាត់",
        recommended_use="Signatory notation, clerk notes, and registrar handwriting simulations.",
        is_heading_font=False,
        google_fonts_family_name="Fasthand",
    ),
]


class TemplateStylerService:
    """Manages document template box styling, font application, and CSS/SVG generation."""

    def get_supported_fonts(self) -> List[SupportedFontDetail]:
        """Returns the authoritative list of supported Khmer fonts."""
        return SUPPORTED_FONTS

    def get_default_template_styles(self, template_name: str = "standard_birth_certificate_v1") -> Dict[str, BoxStyleConfig]:
        """Provides default typography and coordinates for standard civil templates."""
        return {
            "certificate_title": BoxStyleConfig(
                font_family=KhmerFontFamily.KHMER_OS_MOUL_LIGHT,
                font_size_pt=18.0,
                font_weight=FontWeight.BOLD,
                text_color="#1E3A8A",  # Administrative Navy
                text_align=TextAlign.CENTER,
                box_x_pct=20.0,
                box_y_pct=10.0,
                box_width_pct=60.0,
                box_height_pct=5.5,
                border_width_px=0.0,
            ),
            "certificate_no": BoxStyleConfig(
                font_family=KhmerFontFamily.KHMER_OS_BATTAMBANG,
                font_size_pt=11.0,
                font_weight=FontWeight.BOLD,
                text_color="#0F172A",
                text_align=TextAlign.RIGHT,
                box_x_pct=65.0,
                box_y_pct=16.0,
                box_width_pct=25.0,
                box_height_pct=4.0,
                border_width_px=1.0,
                border_color="#CBD5E1",
            ),
            "full_name_km": BoxStyleConfig(
                font_family=KhmerFontFamily.KHMER_OS_BATTAMBANG,
                font_size_pt=14.0,
                font_weight=FontWeight.BOLD,
                text_color="#0F172A",
                text_align=TextAlign.LEFT,
                box_x_pct=28.0,
                box_y_pct=28.0,
                box_width_pct=45.0,
                box_height_pct=5.0,
                border_width_px=1.0,
                border_color="#94A3B8",
            ),
            "full_name_en": BoxStyleConfig(
                font_family=KhmerFontFamily.KHMER_OS_SIEMREAP,
                font_size_pt=12.0,
                font_weight=FontWeight.SEMIBOLD,
                text_color="#1E293B",
                text_align=TextAlign.LEFT,
                box_x_pct=28.0,
                box_y_pct=34.0,
                box_width_pct=45.0,
                box_height_pct=4.5,
                border_width_px=1.0,
                border_color="#CBD5E1",
            ),
            "date_of_birth": BoxStyleConfig(
                font_family=KhmerFontFamily.KHMER_OS_BATTAMBANG,
                font_size_pt=12.0,
                font_weight=FontWeight.NORMAL,
                text_color="#0F172A",
                text_align=TextAlign.LEFT,
                box_x_pct=28.0,
                box_y_pct=40.0,
                box_width_pct=40.0,
                box_height_pct=4.5,
                border_width_px=1.0,
            ),
            "birth_place": BoxStyleConfig(
                font_family=KhmerFontFamily.KHMER_OS_BATTAMBANG,
                font_size_pt=12.5,
                font_weight=FontWeight.NORMAL,
                text_color="#0F172A",
                text_align=TextAlign.LEFT,
                box_x_pct=28.0,
                box_y_pct=46.5,
                box_width_pct=62.0,
                box_height_pct=6.0,
                border_width_px=1.0,
                border_color="#94A3B8",
            ),
            "father_name": BoxStyleConfig(
                font_family=KhmerFontFamily.KHMER_OS_BATTAMBANG,
                font_size_pt=12.0,
                font_weight=FontWeight.NORMAL,
                text_color="#0F172A",
                text_align=TextAlign.LEFT,
                box_x_pct=28.0,
                box_y_pct=54.0,
                box_width_pct=45.0,
                box_height_pct=4.5,
                border_width_px=1.0,
            ),
            "mother_name": BoxStyleConfig(
                font_family=KhmerFontFamily.KHMER_OS_BATTAMBANG,
                font_size_pt=12.0,
                font_weight=FontWeight.NORMAL,
                text_color="#0F172A",
                text_align=TextAlign.LEFT,
                box_x_pct=28.0,
                box_y_pct=60.5,
                box_width_pct=45.0,
                box_height_pct=4.5,
                border_width_px=1.0,
            ),
        }

    def apply_styles_to_document(
        self,
        request: ApplyTemplateStylingRequest,
    ) -> ApplyTemplateStylingResponse:
        """Transforms extracted document fields into styled template boxes with CSS & SVG output."""
        styled_boxes: Dict[str, StyledBoxOutput] = {}
        css_rules: List[str] = [
            "/* Auto-generated Municipal Civil Registry Template Stylesheet */",
            "@import url('https://fonts.googleapis.com/css2?family=Battambang:wght@400;700&family=Bokor&family=Fasthand&family=Kantumruy+Pro:wght@400;600;700&family=Moul&family=Siemreap&display=swap');",
            ".ocr-template-canvas { position: relative; width: 100%; aspect-ratio: 1 / 1.414; background: #FFFFFF; }",
        ]

        svg_elements: List[str] = [
            '<svg viewBox="0 0 1000 1414" xmlns="http://www.w3.org/2000/svg" class="ocr-template-svg">',
            '  <defs>',
            '    <style>',
            "      @import url('https://fonts.googleapis.com/css2?family=Battambang:wght@400;700&family=Bokor&family=Fasthand&family=Kantumruy+Pro:wght@400;600;700&family=Moul&family=Siemreap&display=swap');",
            '      .box-rect { fill: #FFFFFF; stroke-dasharray: 2 2; }',
            '    </style>',
            '  </defs>',
            '  <rect width="1000" height="1414" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="2"/>',
        ]

        for field_key, style in request.field_styles.items():
            val = str(request.document_fields.get(field_key, "")).strip()

            font_family_css = f"'{style.font_family.value}', sans-serif"
            font_weight_val = style.font_weight.value

            # Build CSS inline styles
            inline_css = (
                f"position: absolute; "
                f"left: {style.box_x_pct}%; "
                f"top: {style.box_y_pct}%; "
                f"width: {style.box_width_pct}%; "
                f"height: {style.box_height_pct}%; "
                f"font-family: {font_family_css}; "
                f"font-size: {style.font_size_pt}pt; "
                f"font-weight: {font_weight_val}; "
                f"font-style: {style.font_style}; "
                f"color: {style.text_color}; "
                f"text-align: {style.text_align.value}; "
                f"line-height: {style.line_height}; "
                f"letter-spacing: {style.letter_spacing_px}px; "
                f"background-color: {style.background_color}; "
                f"border: {style.border_width_px}px solid {style.border_color}; "
                f"border-radius: {style.border_radius_px}px; "
                f"padding: {style.padding_px}px; "
                f"box-sizing: border-box; "
                f"z-index: {style.z_index}; "
                f"overflow: hidden;"
            )

            class_name = f"box-{field_key}"
            css_rules.append(
                f".{class_name} {{\n"
                f"  position: absolute;\n"
                f"  left: {style.box_x_pct}%;\n"
                f"  top: {style.box_y_pct}%;\n"
                f"  width: {style.box_width_pct}%;\n"
                f"  height: {style.box_height_pct}%;\n"
                f"  font-family: {font_family_css};\n"
                f"  font-size: {style.font_size_pt}pt;\n"
                f"  font-weight: {font_weight_val};\n"
                f"  color: {style.text_color};\n"
                f"  text-align: {style.text_align.value};\n"
                f"  padding: {style.padding_px}px;\n"
                f"  border: {style.border_width_px}px solid {style.border_color};\n"
                f"  border-radius: {style.border_radius_px}px;\n"
                f"}}\n"
            )

            # Build SVG element (scaled to 1000 x 1414 canvas)
            svg_x = style.box_x_pct * 10.0
            svg_y = style.box_y_pct * 14.14
            svg_w = style.box_width_pct * 10.0
            svg_h = style.box_height_pct * 14.14
            escaped_val = html.escape(val)

            svg_box = (
                f'  <!-- Box: {field_key} -->\n'
                f'  <g id="box_{field_key}">\n'
                f'    <rect x="{svg_x}" y="{svg_y}" width="{svg_w}" height="{svg_h}" '
                f'fill="{style.background_color}" stroke="{style.border_color}" stroke-width="{style.border_width_px}" '
                f'rx="{style.border_radius_px}"/>\n'
                f'    <text x="{svg_x + (style.padding_px * 2)}" y="{svg_y + (svg_h * 0.7)}" '
                f'font-family="{style.font_family.value}" font-size="{style.font_size_pt * 1.33}" '
                f'font-weight="{font_weight_val}" fill="{style.text_color}">{escaped_val}</text>\n'
                f'  </g>'
            )
            svg_elements.append(svg_box)

            styled_boxes[field_key] = StyledBoxOutput(
                field_key=field_key,
                value=val,
                css_style_inline=inline_css,
                css_classes=f"ocr-template-box {class_name}",
                computed_geometry={
                    "x_pct": style.box_x_pct,
                    "y_pct": style.box_y_pct,
                    "width_pct": style.box_width_pct,
                    "height_pct": style.box_height_pct,
                },
                svg_element=svg_box,
            )

        svg_elements.append("</svg>")
        full_svg = "\n".join(svg_elements)
        full_stylesheet = "\n".join(css_rules)

        return ApplyTemplateStylingResponse(
            template_name=request.template_name,
            styled_boxes=styled_boxes,
            full_css_stylesheet=full_stylesheet,
            svg_preview=full_svg,
        )


# Global singleton instance
template_styler_service = TemplateStylerService()
