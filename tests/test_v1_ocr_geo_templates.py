"""Comprehensive Test Suite for v1 OCR, Cambodia Geo, and Template Styling APIs.

Validates:
1. System Health Telemetry (/api/v1/health_check).
2. Multimodal OCR Models and Capabilities (/api/v1/ocr/models).
3. Handwritten Khmer OCR Extraction (/api/v1/ocr/extract-handwritten) with ZDR and bounding boxes.
4. Cambodia Geographic Administrative Hierarchy (/api/v1/geo/provinces, /districts, /communes, /hierarchy).
5. Birthplace Address Resolution & Fuzzy Auto-Correction (/api/v1/geo/validate-birthplace).
6. Official Cambodian Civil Registry Typography Catalog (/api/v1/templates/fonts).
7. Template Box Styling Engine (/api/v1/templates/box-styles/apply) with CSS and SVG vector generation.
8. Integrated Document Verification with Birthplace Gazetteer Cross-Referencing (/api/v1/documents/verify).
"""

import io
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _create_mock_birth_certificate_image() -> bytes:
    """Creates a synthetic Khmer document image in memory for testing."""
    img = np.full((1200, 850, 3), 250, dtype=np.uint8)
    # Add border frame
    cv2.rectangle(img, (30, 30), (820, 1170), (40, 40, 40), 2)
    # Add text-like lines
    cv2.putText(
        img,
        "KINGDOM OF CAMBODIA - NATION RELIGION KING",
        (180, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (20, 20, 20),
        2,
    )
    cv2.putText(
        img,
        "OFFICIAL BIRTH CERTIFICATE NO: BC-2024-009821",
        (150, 140),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (20, 20, 20),
        2,
    )
    success, encoded = cv2.imencode(".png", img)
    assert success, "Failed to encode mock certificate"
    return encoded.tobytes()


# ---------------------------------------------------------------------------
# 1. System Health & Metadata Telemetry
# ---------------------------------------------------------------------------
def test_health_check_endpoint():
    """Validates the /api/v1/health_check endpoint contract."""
    response = client.get("/api/v1/health_check")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "app_version" in data
    assert data["zero_data_retention_enforced"] is True


# ---------------------------------------------------------------------------
# 2. Multimodal OCR Models & Handwritten Extraction
# ---------------------------------------------------------------------------
def test_ocr_model_capabilities_endpoint():
    """Validates /api/v1/ocr/models endpoint reporting supported vision capabilities."""
    response = client.get("/api/v1/ocr/models")
    assert response.status_code == 200
    data = response.json()
    assert "primary_model" in data
    assert "features_supported" in data
    assert "khmer_subscripts_coarticulation" in data["features_supported"]
    assert "cambodia_geo_gazetteer_cross_referencing" in data["features_supported"]
    assert data["authoritative_gazetteer_loaded"] is True


def test_extract_handwritten_document_endpoint():
    """Validates /api/v1/ocr/extract-handwritten with multipart image upload."""
    mock_bytes = _create_mock_birth_certificate_image()
    files = {"file": ("test_cert.png", io.BytesIO(mock_bytes), "image/png")}

    response = client.post("/api/v1/ocr/extract-handwritten", files=files)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["document_type"] == "birth_certificate_standard"
    assert "model_used" in data
    assert "processing_duration_ms" in data
    assert len(data["preprocessing_applied"]) > 0

    # Verify extracted fields
    fields = data["extracted_fields"]
    assert "certificate_no" in fields
    assert "full_name_km" in fields
    assert "birth_place" in fields

    # Verify bounding box relative percentages
    name_field = fields["full_name_km"]
    assert name_field["bounding_box"] is not None
    assert 0.0 <= name_field["bounding_box"]["x_pct"] <= 100.0
    assert 0.0 <= name_field["bounding_box"]["y_pct"] <= 100.0

    # Verify automatic geographic cross-referencing was attached
    assert data["geographic_verification"] is not None
    assert data["geographic_verification"]["is_valid_administrative_path"] is True
    assert data["geographic_verification"]["confidence_score"] > 80.0


# ---------------------------------------------------------------------------
# 3. Cambodia Geographic Administrative Hierarchy & Birthplace Resolution
# ---------------------------------------------------------------------------
def test_geo_provinces_endpoint():
    """Validates /api/v1/geo/provinces returns all 25 official provinces/capitals."""
    response = client.get("/api/v1/geo/provinces")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 25

    # Check for Capital Phnom Penh and major provinces
    province_names_km = [p["name_km"] for p in data]
    assert any("រាជធានីភ្នំពេញ" in name for name in province_names_km)
    assert any("កណ្តាល" in name for name in province_names_km)
    assert any("សៀមរាប" in name for name in province_names_km)
    assert any("បាត់ដំបង" in name for name in province_names_km)


def test_geo_districts_filtering():
    """Validates /api/v1/geo/districts filtering by province_code."""
    # Filter by Phnom Penh (Code: "12")
    response = client.get("/api/v1/geo/districts?province_code=12")
    assert response.status_code == 200
    districts = response.json()
    assert len(districts) > 0
    for d in districts:
        assert d["province_code"] == "12"


def test_geo_validate_birthplace_accurate():
    """Validates /api/v1/geo/validate-birthplace on a standard complete Cambodian address."""
    payload = {
        "raw_birthplace_text": "ភូមិព្រែកតាពៅ សង្កាត់ដើមមៀន ក្រុងតាខ្មៅ ខេត្តកណ្តាល"
    }
    response = client.post("/api/v1/geo/validate-birthplace", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["is_valid_administrative_path"] is True
    assert data["confidence_score"] >= 90.0
    assert data["province"]["name_km"] == "ខេត្តកណ្តាល"
    assert data["district"]["name_km"] == "ក្រុងតាខ្មៅ"
    assert data["commune"]["name_km"] == "សង្កាត់ដើមមៀន"
    assert "ភូមិព្រែកតាពៅ" in data["standardized_address_km"]


def test_geo_validate_birthplace_auto_correction():
    """Validates fuzzy matching and auto-correction on slightly misspelled names."""
    # Intentional slight typo in Ta Khmau & Kandal
    payload = {
        "raw_birthplace_text": "សង្កាត់ដើមមៀន ក្រុងតាខ្មៅ កណ្ដាល"
    }
    response = client.post("/api/v1/geo/validate-birthplace", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["province"]["code"] == "08"
    assert data["district"]["code"] == "0811"
    assert data["confidence_score"] >= 80.0


def test_geo_validate_birthplace_invalid_province():
    """Validates that a non-existent province triggers discrepancy alerts."""
    payload = {
        "raw_birthplace_text": "ភូមិសន្តិភាព ឃុំកោះស ការ៉ាកាស"
    }
    response = client.post("/api/v1/geo/validate-birthplace", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["is_valid_administrative_path"] is False
    assert len(data["discrepancy_alerts"]) > 0


# ---------------------------------------------------------------------------
# 4. Template Box Styling & Typography Engine
# ---------------------------------------------------------------------------
def test_templates_fonts_endpoint():
    """Validates /api/v1/templates/fonts returns the required Cambodian civil fonts."""
    response = client.get("/api/v1/templates/fonts")
    assert response.status_code == 200
    fonts = response.json()
    assert len(fonts) >= 5

    font_names = [f["name"] for f in fonts]
    assert "Khmer OS Battambang" in font_names
    assert "Khmer OS Siemreap" in font_names
    assert "Khmer OS Muol Light" in font_names
    assert "Khmer OS Bokor" in font_names
    assert "Kantumruy Pro" in font_names


def test_templates_presets_endpoint():
    """Validates /api/v1/templates/presets/{template_name} baseline styles."""
    response = client.get("/api/v1/templates/presets/standard_birth_certificate_v1")
    assert response.status_code == 200
    styles = response.json()
    assert "full_name_km" in styles
    assert "birth_place" in styles
    assert styles["full_name_km"]["font_family"] == "Khmer OS Battambang"
    assert styles["certificate_title"]["font_family"] == "Khmer OS Muol Light"


def test_templates_box_styles_apply():
    """Validates /api/v1/templates/box-styles/apply compiles CSS and SVG previews."""
    payload = {
        "template_name": "standard_birth_certificate_v1",
        "field_styles": {
            "full_name_km": {
                "font_family": "Khmer OS Battambang",
                "font_size_pt": 15.0,
                "font_weight": "bold",
                "text_color": "#1E3A8A",
                "text_align": "left",
                "box_x_pct": 25.0,
                "box_y_pct": 30.0,
                "box_width_pct": 50.0,
                "box_height_pct": 6.0,
                "border_color": "#CBD5E1",
                "border_width_px": 1.0,
            },
            "birth_place": {
                "font_family": "Khmer OS Siemreap",
                "font_size_pt": 13.0,
                "font_weight": "normal",
                "text_color": "#0F172A",
                "text_align": "left",
                "box_x_pct": 25.0,
                "box_y_pct": 45.0,
                "box_width_pct": 65.0,
                "box_height_pct": 7.0,
                "border_color": "#CBD5E1",
                "border_width_px": 1.0,
            },
        },
        "document_fields": {
            "full_name_km": "សុខ ចាន់ដារា",
            "birth_place": "ភូមិព្រែកតាពៅ សង្កាត់ដើមមៀន ក្រុងតាខ្មៅ ខេត្តកណ្តាល",
        },
    }

    response = client.post("/api/v1/templates/box-styles/apply", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["template_name"] == "standard_birth_certificate_v1"
    assert "full_name_km" in data["styled_boxes"]
    assert "birth_place" in data["styled_boxes"]

    # Verify CSS inline string contains the requested properties
    fn_box = data["styled_boxes"]["full_name_km"]
    assert "Khmer OS Battambang" in fn_box["css_style_inline"]
    assert "font-weight: bold" in fn_box["css_style_inline"]
    assert "font-size: 15.0pt" in fn_box["css_style_inline"]
    assert "color: #1E3A8A" in fn_box["css_style_inline"]

    # Verify SVG preview was generated
    assert "<svg" in data["svg_preview"]
    assert "box_full_name_km" in data["svg_preview"]
    assert "សុខ ចាន់ដារា" in data["svg_preview"]


# ---------------------------------------------------------------------------
# 5. Integrated Document Verification with Geographic Cross-Referencing
# ---------------------------------------------------------------------------
def test_document_verify_with_geographic_resolution():
    """Validates /api/v1/documents/verify integrates birthplace gazetteer validation."""
    payload = {
        "extracted_fields": {
            "national_id": "1204009821",
            "certificate_no": "BC-2024-009821",
            "full_name_km": "សុខ ចាន់ដារា",
            "full_name_en": "SOK CHANDARA",
            "birth_place": "ភូមិព្រែកតាពៅ សង្កាត់ដើមមៀន ក្រុងតាខ្មៅ ខេត្តកណ្តាល",
            "district_office": "ដូនពេញ (Daun Penh)",
        }
    }

    response = client.post("/api/v1/documents/verify", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["confidence_level"] >= 85.0
    assert "birth_place" in data["verified_fields"]
    assert data["audit_hash"] is not None
