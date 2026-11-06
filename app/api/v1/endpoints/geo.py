"""Cambodia Geographic Administrative Verification API Endpoints.

Architectural and Security Rationale:
- Exposes endpoints to cross-reference AI-extracted text against the official 25 Provinces/Capitals,
  Districts/Khans/Krongs, Communes/Sangkats, and Villages/Phums of Cambodia.
- Powers hierarchical dropdown cascading for frontend administrative forms.
- Performs fuzzy resolution and auto-correction via RapidFuzz.
- Zero Data Retention: All operations run in memory with zero persistence.
- Strict snake_case naming throughout.
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.geo import (
    GeoEntityCreate,
    GeoEntityUpdate,
    GeoReportCreate,
    GeoReportItem,
    GeoReportListResponse,
    GeoReportUpdate,
    PaginatedGeoEntitiesResponse,
    ProvinceSummary,
    ValidateBirthplaceRequest,
    ValidateBirthplaceResponse,
)
from app.services.cambodia_geo_service import cambodia_geo_service
from app.services.geo_report_service import geo_report_service

logger = logging.getLogger("district_geo_endpoint")

geo_router = APIRouter(
    prefix="/geo",
    tags=["cambodia_geographic_verification"],
)


@geo_router.post(
    "/validate-birthplace",
    response_model=ValidateBirthplaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate Extracted Birthplace Against National Gazetteer",
    description=(
        "Cross-references extracted handwritten or printed birthplace text against the official "
        "Cambodian administrative gazetteer. Resolves provinces, districts, communes, and villages, "
        "auto-corrects minor OCR spelling variations (>= 85%), and returns discrepancy alerts."
    ),
)
async def validate_birthplace_text(payload: ValidateBirthplaceRequest) -> ValidateBirthplaceResponse:
    """Validates and standardizes a Cambodian administrative birthplace address."""
    # Synthesize raw query if individual levels were submitted
    raw_query = payload.raw_birthplace_text
    if not raw_query:
        parts = []
        if payload.village:
            parts.append(payload.village)
        if payload.commune:
            parts.append(payload.commune)
        if payload.district:
            parts.append(payload.district)
        if payload.province:
            parts.append(payload.province)
        raw_query = " ".join(parts)

    if not raw_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'raw_birthplace_text' or administrative division components must be provided.",
        )

    result = cambodia_geo_service.resolve_birthplace_address(raw_query)
    return ValidateBirthplaceResponse(**result)


@geo_router.get(
    "/provinces",
    response_model=List[ProvinceSummary],
    status_code=status.HTTP_200_OK,
    summary="List All 25 Provinces and Capitals of Cambodia",
    description="Returns the authoritative list of Cambodian Provinces/Capitals with NIS codes and names.",
)
async def list_provinces() -> List[ProvinceSummary]:
    """Retrieves all 25 official Provinces/Capitals."""
    provinces = cambodia_geo_service.provinces
    summaries = []
    for prov in provinces:
        # Count associated districts
        d_count = sum(1 for d in cambodia_geo_service.districts if d["province_code"] == prov["code"])
        summaries.append(
            ProvinceSummary(
                code=prov["code"],
                name_km=prov["name_km"],
                name_en=prov["name_en"],
                type=prov.get("type", "Province"),
                district_count=d_count,
            )
        )
    return summaries


@geo_router.get(
    "/districts",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="List Districts / Khans / Krongs",
    description="Retrieves administrative districts, optionally filtered by parent province code.",
)
async def list_districts(
    province_code: Optional[str] = Query(None, description="2-digit Province Code (e.g. '12' for Phnom Penh)"),
) -> List[Dict[str, Any]]:
    """Retrieves districts filtered by province."""
    districts = cambodia_geo_service.districts
    if province_code:
        districts = [d for d in districts if d["province_code"] == province_code]
    return districts


@geo_router.get(
    "/communes",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="List Communes / Sangkats",
    description="Retrieves administrative communes/sangkats, optionally filtered by district code.",
)
async def list_communes(
    district_code: Optional[str] = Query(None, description="4-digit District Code (e.g. '1201' for Chamkar Mon)"),
) -> List[Dict[str, Any]]:
    """Retrieves communes filtered by district."""
    communes = cambodia_geo_service.communes
    if district_code:
        communes = [c for c in communes if c["district_code"] == district_code]
    return communes


@geo_router.get(
    "/hierarchy",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Full Geographic Hierarchy Summary",
    description="Returns aggregate counts and top-level hierarchy of the Cambodian administrative tree.",
)
async def get_geographic_hierarchy_summary() -> Dict[str, Any]:
    """Returns top-level metadata of the indexed Cambodian gazetteer."""
    return {
        "status": "ready",
        "total_provinces": len(cambodia_geo_service.provinces),
        "total_districts": len(cambodia_geo_service.districts),
        "total_communes": len(cambodia_geo_service.communes),
        "total_villages": len(cambodia_geo_service.villages),
        "authoritative_sources": [
            "National Institute of Statistics (NIS)",
            "Ministry of Interior (MoI) Department of General Administration",
            "Sub-Decree on Civil Status and Identification",
        ],
    }


@geo_router.get(
    "/villages",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="List Villages / Phums",
    description="Retrieves administrative villages/phums, optionally filtered by commune code.",
)
async def list_villages(
    commune_code: Optional[str] = Query(None, description="6-digit Commune Code"),
) -> List[Dict[str, Any]]:
    """Retrieves villages filtered by commune."""
    return cambodia_geo_service.get_villages(commune_code=commune_code)


@geo_router.get(
    "/entities",
    response_model=PaginatedGeoEntitiesResponse,
    status_code=status.HTTP_200_OK,
    summary="Search, Filter, Sort, and Paginate Administrative Divisions",
    description="Powers tabular grid views for searching and managing Provinces, Districts, Communes, and Villages.",
)
async def get_paginated_entities(
    level: str = Query("all", description="Filter tier: 'all', 'province', 'district', 'commune', or 'village'"),
    search: Optional[str] = Query(None, description="Search keyword matching code, Khmer name, Latin name, or parent"),
    parent_code: Optional[str] = Query(None, description="Filter by parent division code"),
    province_code: Optional[str] = Query(None, description="Filter specifically by Province code"),
    district_code: Optional[str] = Query(None, description="Filter specifically by District code"),
    commune_code: Optional[str] = Query(None, description="Filter specifically by Commune code"),
    sort_by: str = Query("code", description="Sort column: 'code', 'name_km', 'name_en', 'level', 'type'"),
    sort_order: str = Query("asc", description="Sort direction: 'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(15, ge=1, le=100, description="Rows per page"),
) -> PaginatedGeoEntitiesResponse:
    """Returns paginated administrative divisions matching the search and sort criteria."""
    result = cambodia_geo_service.get_paginated_entities(
        level=level,
        search=search,
        parent_code=parent_code,
        province_code=province_code,
        district_code=district_code,
        commune_code=commune_code,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    return PaginatedGeoEntitiesResponse(**result)


@geo_router.post(
    "/entities",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create a New Administrative Division",
    description="Adds a new Province, District, Commune, or Village to the official national hierarchy.",
)
async def create_geographic_entity(payload: GeoEntityCreate) -> Dict[str, Any]:
    """Creates a new administrative entity."""
    try:
        new_entity = cambodia_geo_service.create_entity(
            level=payload.level,
            code=payload.code,
            name_km=payload.name_km,
            name_en=payload.name_en,
            parent_code=payload.parent_code,
            type_val=payload.type,
        )
        return {
            "status": "success",
            "message": f"Successfully created {payload.level} '{payload.name_km}' ({payload.code})",
            "entity": new_entity,
        }
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except Exception as err:
        logger.error("Failed to create geographic entity: %s", str(err), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save administrative division. Please check inputs and retry.",
        )


@geo_router.put(
    "/entities/{level}/{code}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Update an Existing Administrative Division",
    description="Updates the Khmer name, Latin transliteration, and type of a designated division.",
)
async def update_geographic_entity(
    level: str,
    code: str,
    payload: GeoEntityUpdate,
) -> Dict[str, Any]:
    """Updates an administrative division."""
    updated = cambodia_geo_service.update_entity(
        level=level,
        code=code,
        name_km=payload.name_km,
        name_en=payload.name_en,
        type_val=payload.type,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Administrative entity '{code}' of level '{level}' was not found.",
        )
    return {
        "status": "success",
        "message": f"Successfully updated {level} '{payload.name_km}' ({code})",
        "entity": updated,
    }


@geo_router.delete(
    "/entities/{level}/{code}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Delete an Administrative Division",
    description="Deletes an administrative division and cascades to nested children if applicable.",
)
async def delete_geographic_entity(
    level: str,
    code: str,
) -> Dict[str, Any]:
    """Deletes an administrative division."""
    deleted = cambodia_geo_service.delete_entity(level=level, code=code)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Administrative entity '{code}' of level '{level}' was not found.",
        )
    return {
        "status": "success",
        "message": f"Successfully removed {level} division '{code}' from the national hierarchy.",
        "code": code,
        "level": level,
    }


# ==============================================================================
# Administrative Division Error Reports & Notifications (User -> Admin Flow)
# ==============================================================================


@geo_router.post(
    "/reports",
    response_model=GeoReportItem,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an Administrative Division Error Report",
    description="Allows users or civil registry officers to report naming, spelling, or boundary discrepancies.",
)
async def submit_division_report(payload: GeoReportCreate) -> GeoReportItem:
    """Submits a report to the System Administrator."""
    report = geo_report_service.create_report(
        division_code=payload.division_code,
        division_level=payload.division_level,
        current_name_km=payload.current_name_km,
        current_name_en=payload.current_name_en,
        issue_type=payload.issue_type,
        suggested_name_km=payload.suggested_name_km,
        suggested_name_en=payload.suggested_name_en,
        notes=payload.notes,
        reported_by=payload.reported_by or "user",
    )
    return GeoReportItem(**report)


@geo_router.get(
    "/reports",
    response_model=GeoReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Administrative Division Reports and Notification Badge",
    description="Retrieves submitted reports and pending notification count for system administrators.",
)
async def list_division_reports(
    status_filter: Optional[str] = Query(None, description="Filter: 'all', 'pending', 'read', or 'resolved'"),
) -> GeoReportListResponse:
    """Returns all submitted reports with unread counts."""
    data = geo_report_service.list_reports(status_filter=status_filter)
    return GeoReportListResponse(**data)


@geo_router.patch(
    "/reports/{report_id}",
    response_model=GeoReportItem,
    status_code=status.HTTP_200_OK,
    summary="Update Report Status (Mark as Read or Resolved)",
    description="Updates status of an administrative report (e.g. 'read', 'resolved') with optional admin notes.",
)
async def update_division_report_status(
    report_id: str,
    payload: GeoReportUpdate,
) -> GeoReportItem:
    """Updates a report's lifecycle status."""
    updated = geo_report_service.update_report(
        report_id=report_id,
        new_status=payload.status,
        admin_notes=payload.admin_notes,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' was not found.",
        )
    return GeoReportItem(**updated)


@geo_router.delete(
    "/reports/{report_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Delete an Administrative Report",
)
async def delete_division_report(report_id: str) -> Dict[str, Any]:
    """Deletes a report by ID."""
    deleted = geo_report_service.delete_report(report_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID '{report_id}' was not found.",
        )
    return {
        "status": "success",
        "message": f"Report '{report_id}' has been removed.",
        "id": report_id,
    }

