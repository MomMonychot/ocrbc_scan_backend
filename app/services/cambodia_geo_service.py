"""Cambodia Geographic Administrative Hierarchy Reference & Fuzzy Matching Service.

Architectural Rationale:
- Loads the authoritative Gazetteer of Cambodia (25 Provinces/Capitals, Districts/Khans/Municipalities,
  Communes/Sangkats, and Villages/Phums).
- Provides high-performance fuzzy matching via RapidFuzz to cross-reference AI-extracted handwritten
  birthplace text against official National Institute of Statistics (NIS) & Ministry of Interior administrative codes.
- Strictly adheres to Zero-Data-Retention (ZDR) and snake_case conventions.
"""

import json
import logging
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from rapidfuzz import fuzz, process

logger = logging.getLogger("district_cambodia_geo_service")

GEO_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cambodia_geographic_hierarchy.json"


class CambodiaGeoService:
    """Authoritative geographic lookup and fuzzy resolution service."""

    def __init__(self, data_path: Path = GEO_DATA_PATH) -> None:
        self.data_path = data_path
        self._raw_data: Dict[str, Any] = {"version": "2026.1", "provinces": []}
        self.provinces: List[Dict[str, Any]] = []
        self.districts: List[Dict[str, Any]] = []
        self.communes: List[Dict[str, Any]] = []
        self.villages: List[Dict[str, Any]] = []

        # Inverted index names for fast rapidfuzz candidate matching
        self._prov_km_list: List[str] = []
        self._dist_km_list: List[str] = []
        self._comm_km_list: List[str] = []
        self._vill_km_list: List[str] = []

        self._load_and_index()

    def _load_and_index(self) -> None:
        """Parses and indexes the administrative geography file in memory."""
        if not self.data_path.exists():
            logger.error("Authoritative geography file not found at %s", self.data_path)
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        self._raw_data = raw
        self.provinces = []
        self.districts = []
        self.communes = []
        self.villages = []
        self._prov_km_list = []
        self._dist_km_list = []
        self._comm_km_list = []
        self._vill_km_list = []

        for prov in raw.get("provinces", []):
            prov_entry = {
                "code": prov["code"],
                "name_km": prov["name_km"],
                "name_en": prov["name_en"],
                "type": prov.get("type", "Province"),
                "level": "province",
                "parent_name_km": "ព្រះរាជាណាចក្រកម្ពុជា",
                "parent_name_en": "Kingdom of Cambodia",
                "parent_code": "KH",
            }
            self.provinces.append(prov_entry)
            self._prov_km_list.append(prov["name_km"])

            for dist in prov.get("districts", []):
                dist_entry = {
                    "code": dist["code"],
                    "name_km": dist["name_km"],
                    "name_en": dist["name_en"],
                    "type": dist.get("type", "District"),
                    "level": "district",
                    "province_code": prov["code"],
                    "province_name_km": prov["name_km"],
                    "province_name_en": prov["name_en"],
                    "parent_name_km": prov["name_km"],
                    "parent_name_en": prov["name_en"],
                    "parent_code": prov["code"],
                }
                self.districts.append(dist_entry)
                self._dist_km_list.append(dist["name_km"])

                for comm in dist.get("communes", []):
                    comm_entry = {
                        "code": comm["code"],
                        "name_km": comm["name_km"],
                        "name_en": comm["name_en"],
                        "type": comm.get("type", "Commune"),
                        "level": "commune",
                        "district_code": dist["code"],
                        "district_name_km": dist["name_km"],
                        "province_code": prov["code"],
                        "province_name_km": prov["name_km"],
                        "parent_name_km": f"{prov['name_km']} > {dist['name_km']}",
                        "parent_name_en": f"{prov['name_en']} > {dist['name_en']}",
                        "parent_code": dist["code"],
                    }
                    self.communes.append(comm_entry)
                    self._comm_km_list.append(comm["name_km"])

                    for vill in comm.get("villages", []):
                        vill_entry = {
                            "code": vill["code"],
                            "name_km": vill["name_km"],
                            "name_en": vill["name_en"],
                            "type": vill.get("type", "Village"),
                            "level": "village",
                            "commune_code": comm["code"],
                            "commune_name_km": comm["name_km"],
                            "district_code": dist["code"],
                            "province_code": prov["code"],
                            "parent_name_km": f"{dist['name_km']} > {comm['name_km']}",
                            "parent_name_en": f"{dist['name_en']} > {comm['name_en']}",
                            "parent_code": comm["code"],
                        }
                        self.villages.append(vill_entry)
                        self._vill_km_list.append(vill["name_km"])

        logger.info(
            "Cambodia Geography Service ready: %d provinces, %d districts, %d communes, %d villages indexed",
            len(self.provinces),
            len(self.districts),
            len(self.communes),
            len(self.villages),
        )

    def save_to_disk(self) -> None:
        """Persists in-memory hierarchy changes to JSON gazetteer on disk."""
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self._raw_data, f, ensure_ascii=False, indent=2)
        logger.info("Administrative gazetteer successfully persisted to %s", self.data_path)

    def get_villages(self, commune_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves villages, optionally filtered by commune."""
        if commune_code:
            return [v for v in self.villages if v.get("commune_code") == commune_code]
        return self.villages

    def get_paginated_entities(
        self,
        level: str = "all",
        search: Optional[str] = None,
        parent_code: Optional[str] = None,
        sort_by: str = "code",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 15,
    ) -> Dict[str, Any]:
        """Filters, sorts, and paginates administrative divisions for tabular rendering."""
        # 1. Gather candidates according to requested tier
        candidates: List[Dict[str, Any]] = []
        lvl = (level or "all").lower()
        if lvl == "province":
            candidates = list(self.provinces)
        elif lvl == "district":
            candidates = list(self.districts)
        elif lvl == "commune":
            candidates = list(self.communes)
        elif lvl == "village":
            candidates = list(self.villages)
        else:
            candidates = list(self.provinces) + list(self.districts) + list(self.communes) + list(self.villages)

        # 2. Filter by parent_code if given
        if parent_code:
            p_code = str(parent_code).strip()
            candidates = [
                c
                for c in candidates
                if c.get("parent_code") == p_code
                or c.get("province_code") == p_code
                or c.get("district_code") == p_code
                or c.get("commune_code") == p_code
            ]

        # 3. Filter by search query (code, name_km, name_en, parent names)
        if search:
            q = str(search).strip().lower()
            candidates = [
                c
                for c in candidates
                if q in str(c.get("code", "")).lower()
                or q in str(c.get("name_km", "")).lower()
                or q in str(c.get("name_en", "")).lower()
                or q in str(c.get("parent_name_km", "")).lower()
                or q in str(c.get("parent_name_en", "")).lower()
            ]

        # 4. Sorting
        reverse = sort_order.lower() == "desc"
        valid_sort_keys = ["code", "name_km", "name_en", "level", "type", "parent_code"]
        key = sort_by if sort_by in valid_sort_keys else "code"

        def _sort_key(item: Dict[str, Any]):
            val = item.get(key, "")
            return str(val).lower() if val is not None else ""

        candidates.sort(key=_sort_key, reverse=reverse)

        # 5. Pagination
        total = len(candidates)
        safe_page_size = max(1, min(100, page_size))
        total_pages = max(1, math.ceil(total / safe_page_size))
        current_page = max(1, min(page, total_pages))

        start_idx = (current_page - 1) * safe_page_size
        end_idx = start_idx + safe_page_size
        page_items = candidates[start_idx:end_idx]

        return {
            "total": total,
            "page": current_page,
            "page_size": safe_page_size,
            "total_pages": total_pages,
            "items": page_items,
        }

    def update_entity(
        self,
        level: str,
        code: str,
        name_km: str,
        name_en: str,
        type_val: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Updates an administrative division's names and re-indexes."""
        lvl = level.lower()
        found = False

        if lvl == "province":
            for prov in self._raw_data.get("provinces", []):
                if prov["code"] == code:
                    prov["name_km"] = name_km
                    prov["name_en"] = name_en
                    if type_val:
                        prov["type"] = type_val
                    found = True
                    break

        elif lvl == "district":
            for prov in self._raw_data.get("provinces", []):
                for dist in prov.get("districts", []):
                    if dist["code"] == code:
                        dist["name_km"] = name_km
                        dist["name_en"] = name_en
                        if type_val:
                            dist["type"] = type_val
                        found = True
                        break
                if found:
                    break

        elif lvl == "commune":
            for prov in self._raw_data.get("provinces", []):
                for dist in prov.get("districts", []):
                    for comm in dist.get("communes", []):
                        if comm["code"] == code:
                            comm["name_km"] = name_km
                            comm["name_en"] = name_en
                            if type_val:
                                comm["type"] = type_val
                            found = True
                            break
                    if found:
                        break
                if found:
                    break

        elif lvl == "village":
            for prov in self._raw_data.get("provinces", []):
                for dist in prov.get("districts", []):
                    for comm in dist.get("communes", []):
                        for vill in comm.get("villages", []):
                            if vill["code"] == code:
                                vill["name_km"] = name_km
                                vill["name_en"] = name_en
                                if type_val:
                                    vill["type"] = type_val
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break
                if found:
                    break

        if not found:
            return None

        self.save_to_disk()
        self._load_and_index()
        return {"code": code, "level": lvl, "name_km": name_km, "name_en": name_en, "type": type_val}

    def delete_entity(self, level: str, code: str) -> bool:
        """Deletes an administrative division and re-indexes."""
        lvl = level.lower()
        found = False

        if lvl == "province":
            provinces = self._raw_data.get("provinces", [])
            for idx, p in enumerate(provinces):
                if p["code"] == code:
                    del provinces[idx]
                    found = True
                    break

        elif lvl == "district":
            for prov in self._raw_data.get("provinces", []):
                districts = prov.get("districts", [])
                for idx, d in enumerate(districts):
                    if d["code"] == code:
                        del districts[idx]
                        found = True
                        break
                if found:
                    break

        elif lvl == "commune":
            for prov in self._raw_data.get("provinces", []):
                for dist in prov.get("districts", []):
                    communes = dist.get("communes", [])
                    for idx, c in enumerate(communes):
                        if c["code"] == code:
                            del communes[idx]
                            found = True
                            break
                    if found:
                        break
                if found:
                    break

        elif lvl == "village":
            for prov in self._raw_data.get("provinces", []):
                for dist in prov.get("districts", []):
                    for comm in dist.get("communes", []):
                        villages = comm.get("villages", [])
                        for idx, v in enumerate(villages):
                            if v["code"] == code:
                                del villages[idx]
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break
                if found:
                    break

        if not found:
            return False

        self.save_to_disk()
        self._load_and_index()
        return True

    def create_entity(
        self,
        level: str,
        code: str,
        name_km: str,
        name_en: str,
        parent_code: Optional[str] = None,
        type_val: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new administrative division under its designated parent."""
        lvl = level.lower()

        # Check for duplicate code
        all_codes = [p["code"] for p in self.provinces] + [d["code"] for d in self.districts] + [c["code"] for c in self.communes] + [v["code"] for v in self.villages]
        if code in all_codes:
            raise ValueError(f"Administrative division with code '{code}' already exists.")

        if lvl == "province":
            new_prov = {
                "code": code,
                "name_km": name_km,
                "name_en": name_en,
                "type": type_val or "Province",
                "districts": [],
            }
            self._raw_data.setdefault("provinces", []).append(new_prov)

        elif lvl == "district":
            if not parent_code:
                raise ValueError("Parent province code is required to create a district.")
            parent_prov = next((p for p in self._raw_data.get("provinces", []) if p["code"] == parent_code), None)
            if not parent_prov:
                raise ValueError(f"Parent province with code '{parent_code}' not found.")
            new_dist = {
                "code": code,
                "name_km": name_km,
                "name_en": name_en,
                "type": type_val or "District",
                "communes": [],
            }
            parent_prov.setdefault("districts", []).append(new_dist)

        elif lvl == "commune":
            if not parent_code:
                raise ValueError("Parent district code is required to create a commune.")
            parent_dist = None
            for p in self._raw_data.get("provinces", []):
                for d in p.get("districts", []):
                    if d["code"] == parent_code:
                        parent_dist = d
                        break
                if parent_dist:
                    break
            if not parent_dist:
                raise ValueError(f"Parent district with code '{parent_code}' not found.")
            new_comm = {
                "code": code,
                "name_km": name_km,
                "name_en": name_en,
                "type": type_val or "Commune",
                "villages": [],
            }
            parent_dist.setdefault("communes", []).append(new_comm)

        elif lvl == "village":
            if not parent_code:
                raise ValueError("Parent commune code is required to create a village.")
            parent_comm = None
            for p in self._raw_data.get("provinces", []):
                for d in p.get("districts", []):
                    for c in d.get("communes", []):
                        if c["code"] == parent_code:
                            parent_comm = c
                            break
                    if parent_comm:
                        break
                if parent_comm:
                    break
            if not parent_comm:
                raise ValueError(f"Parent commune with code '{parent_code}' not found.")
            new_vill = {
                "code": code,
                "name_km": name_km,
                "name_en": name_en,
                "type": type_val or "Village",
            }
            parent_comm.setdefault("villages", []).append(new_vill)
        else:
            raise ValueError(f"Invalid level '{level}'. Must be province, district, commune, or village.")

        self.save_to_disk()
        self._load_and_index()
        return {
            "code": code,
            "level": lvl,
            "name_km": name_km,
            "name_en": name_en,
            "parent_code": parent_code,
            "type": type_val,
        }

    def clean_prefix(self, name: str) -> str:
        """Strips administrative prefixes for invariant fuzzy score calculation."""
        prefixes = [
            "រាជធានី",
            "ខេត្ត",
            "ក្រុង",
            "ស្រុក",
            "ខណ្ឌ",
            "សង្កាត់",
            "ឃុំ",
            "ភូមិ",
            "Province",
            "District",
            "Khan",
            "Krong",
            "Sangkat",
            "Commune",
            "Phum",
        ]
        cleaned = name.strip()
        for p in prefixes:
            if cleaned.startswith(p):
                cleaned = cleaned[len(p) :].strip()
        return cleaned

    def match_province(self, query: str, threshold: float = 70.0) -> Optional[Tuple[Dict[str, Any], float]]:
        """Finds closest matching Province / Capital."""
        if not query:
            return None
        cleaned_query = self.clean_prefix(query)
        best_match = None
        best_score = 0.0

        for prov in self.provinces:
            raw_ratio = fuzz.ratio(query, prov["name_km"])
            cleaned_ratio = fuzz.token_set_ratio(cleaned_query, self.clean_prefix(prov["name_km"]))
            en_ratio = fuzz.ratio(query.lower(), prov["name_en"].lower())
            score = max(raw_ratio, cleaned_ratio, en_ratio)
            if score > best_score:
                best_score = score
                best_match = prov

        if best_match and best_score >= threshold:
            return best_match, round(best_score, 1)
        return None

    def match_district(
        self,
        query: str,
        province_code: Optional[str] = None,
        threshold: float = 70.0,
    ) -> Optional[Tuple[Dict[str, Any], float]]:
        """Finds closest matching District / Khan / Krong within an optional parent province."""
        if not query:
            return None
        cleaned_query = self.clean_prefix(query)
        candidates = self.districts
        if province_code:
            candidates = [d for d in self.districts if d["province_code"] == province_code]

        best_match = None
        best_score = 0.0
        for dist in candidates:
            raw_ratio = fuzz.ratio(query, dist["name_km"])
            cleaned_ratio = fuzz.token_set_ratio(cleaned_query, self.clean_prefix(dist["name_km"]))
            en_ratio = fuzz.ratio(query.lower(), dist["name_en"].lower())
            score = max(raw_ratio, cleaned_ratio, en_ratio)
            if score > best_score:
                best_score = score
                best_match = dist

        if best_match and best_score >= threshold:
            return best_match, round(best_score, 1)
        return None

    def match_commune(
        self,
        query: str,
        district_code: Optional[str] = None,
        threshold: float = 70.0,
    ) -> Optional[Tuple[Dict[str, Any], float]]:
        """Finds closest matching Commune / Sangkat within an optional parent district."""
        if not query:
            return None
        cleaned_query = self.clean_prefix(query)
        candidates = self.communes
        if district_code:
            candidates = [c for c in self.communes if c["district_code"] == district_code]

        best_match = None
        best_score = 0.0
        for comm in candidates:
            raw_ratio = fuzz.ratio(query, comm["name_km"])
            cleaned_ratio = fuzz.token_set_ratio(cleaned_query, self.clean_prefix(comm["name_km"]))
            en_ratio = fuzz.ratio(query.lower(), comm["name_en"].lower())
            score = max(raw_ratio, cleaned_ratio, en_ratio)
            if score > best_score:
                best_score = score
                best_match = comm

        if best_match and best_score >= threshold:
            return best_match, round(best_score, 1)
        return None

    def match_village(
        self,
        query: str,
        commune_code: Optional[str] = None,
        threshold: float = 70.0,
    ) -> Optional[Tuple[Dict[str, Any], float]]:
        """Finds closest matching Village / Phum within an optional parent commune."""
        if not query:
            return None
        cleaned_query = self.clean_prefix(query)
        candidates = self.villages
        if commune_code:
            candidates = [v for v in self.villages if v["commune_code"] == commune_code]

        best_match = None
        best_score = 0.0
        for vill in candidates:
            raw_ratio = fuzz.ratio(query, vill["name_km"])
            cleaned_ratio = fuzz.token_set_ratio(cleaned_query, self.clean_prefix(vill["name_km"]))
            en_ratio = fuzz.ratio(query.lower(), vill["name_en"].lower())
            score = max(raw_ratio, cleaned_ratio, en_ratio)
            if score > best_score:
                best_score = score
                best_match = vill

        if best_match and best_score >= threshold:
            return best_match, round(best_score, 1)
        return None

    def resolve_birthplace_address(self, raw_birthplace_text: str) -> Dict[str, Any]:
        """Cross-references and validates an extracted birthplace text string.

        Args:
            raw_birthplace_text: Full raw text extracted by AI (e.g. 'ភូមិព្រែកតាពៅ សង្កាត់ដើមមៀន ក្រុងតាខ្មៅ ខេត្តកណ្តាល')

        Returns:
            Structured verification report with:
            - is_valid_administrative_path (bool)
            - confidence_score (float)
            - province (dict with code, name_km, name_en, score)
            - district (dict with code, name_km, name_en, score)
            - commune (dict with code, name_km, name_en, score)
            - village (dict with code, name_km, name_en, score)
            - standardized_address_km (str)
            - standardized_address_en (str)
            - auto_corrected (bool)
            - discrepancy_alerts (list of warning strings)
        """
        raw = str(raw_birthplace_text or "").strip()
        if not raw:
            return {
                "is_valid_administrative_path": False,
                "confidence_score": 0.0,
                "province": None,
                "district": None,
                "commune": None,
                "village": None,
                "standardized_address_km": "",
                "standardized_address_en": "",
                "auto_corrected": False,
                "discrepancy_alerts": ["Empty birthplace string submitted."],
            }

        # Extract tokens matching administrative levels
        # Match Province / Capital (ខេត្ត... or រាជធានី...)
        prov_match = re.search(r"(?:ខេត្ត|រាជធានី)\s*([^\s,]+)", raw)
        # Match District / Khan / Krong (ស្រុក... or ខណ្ឌ... or ក្រុង...)
        dist_match = re.search(r"(?:ស្រុក|ខណ្ឌ|ក្រុង)\s*([^\s,]+)", raw)
        # Match Commune / Sangkat (ឃុំ... or សង្កាត់...)
        comm_match = re.search(r"(?:ឃុំ|សង្កាត់)\s*([^\s,]+)", raw)
        # Match Village (ភូមិ...)
        vill_match = re.search(r"(?:ភូមិ)\s*([^\s,]+)", raw)

        # 1. Resolve Province
        prov_candidate = prov_match.group(0) if prov_match else raw
        prov_res = self.match_province(prov_candidate, threshold=60.0)
        prov_obj = None
        prov_score = 0.0
        prov_code = None

        if prov_res:
            prov_obj, prov_score = prov_res
            prov_code = prov_obj["code"]

        # 2. Resolve District (hierarchically under resolved province if known)
        dist_candidate = dist_match.group(0) if dist_match else raw
        dist_res = self.match_district(dist_candidate, province_code=prov_code, threshold=60.0)
        dist_obj = None
        dist_score = 0.0
        dist_code = None

        if dist_res:
            dist_obj, dist_score = dist_res
            dist_code = dist_obj["code"]
            # If province wasn't found before, back-fill from district!
            if not prov_obj and dist_obj.get("province_code"):
                prov_code = dist_obj["province_code"]
                for p in self.provinces:
                    if p["code"] == prov_code:
                        prov_obj = p
                        prov_score = dist_score
                        break

        # 3. Resolve Commune (hierarchically under resolved district if known)
        comm_candidate = comm_match.group(0) if comm_match else raw
        comm_res = self.match_commune(comm_candidate, district_code=dist_code, threshold=60.0)
        comm_obj = None
        comm_score = 0.0
        comm_code = None

        if comm_res:
            comm_obj, comm_score = comm_res
            comm_code = comm_obj["code"]
            if not dist_obj and comm_obj.get("district_code"):
                dist_code = comm_obj["district_code"]
                for d in self.districts:
                    if d["code"] == dist_code:
                        dist_obj = d
                        dist_score = comm_score
                        break

        # 4. Resolve Village
        vill_candidate = vill_match.group(0) if vill_match else raw
        vill_res = self.match_village(vill_candidate, commune_code=comm_code, threshold=60.0)
        vill_obj = None
        vill_score = 0.0

        if vill_res:
            vill_obj, vill_score = vill_res

        # Calculate weighted average confidence
        scores = []
        if prov_score > 0:
            scores.append(prov_score)
        if dist_score > 0:
            scores.append(dist_score)
        if comm_score > 0:
            scores.append(comm_score)
        if vill_score > 0:
            scores.append(vill_score)

        avg_confidence = round(sum(scores) / len(scores), 1) if scores else 0.0

        # Build standardized addresses
        km_parts = []
        en_parts = []
        if vill_obj:
            km_parts.append(vill_obj["name_km"])
            en_parts.append(vill_obj["name_en"])
        elif vill_match:
            km_parts.append(vill_match.group(0))
            en_parts.append(vill_match.group(0))

        if comm_obj:
            km_parts.append(comm_obj["name_km"])
            en_parts.append(comm_obj["name_en"])
        if dist_obj:
            km_parts.append(dist_obj["name_km"])
            en_parts.append(dist_obj["name_en"])
        if prov_obj:
            km_parts.append(prov_obj["name_km"])
            en_parts.append(prov_obj["name_en"])

        std_km = " ".join(km_parts)
        std_en = ", ".join(en_parts)

        # Discrepancy checks
        alerts: List[str] = []
        is_valid = True

        if not prov_obj:
            alerts.append("Province / Capital could not be verified against the official national registry.")
            is_valid = False
        if not dist_obj:
            alerts.append("District / Khan / Krong could not be verified in the national gazetteer.")
            is_valid = False
        if not comm_obj:
            alerts.append("Commune / Sangkat could not be verified in the municipal hierarchy.")
            is_valid = False

        # Auto-correction is triggered if matching confidence is high (>= 85%)
        auto_corrected = avg_confidence >= 85.0 and std_km != raw

        return {
            "is_valid_administrative_path": is_valid,
            "confidence_score": avg_confidence,
            "province": {
                "code": prov_obj["code"] if prov_obj else None,
                "name_km": prov_obj["name_km"] if prov_obj else None,
                "name_en": prov_obj["name_en"] if prov_obj else None,
                "score": prov_score,
            }
            if prov_obj
            else None,
            "district": {
                "code": dist_obj["code"] if dist_obj else None,
                "name_km": dist_obj["name_km"] if dist_obj else None,
                "name_en": dist_obj["name_en"] if dist_obj else None,
                "score": dist_score,
            }
            if dist_obj
            else None,
            "commune": {
                "code": comm_obj["code"] if comm_obj else None,
                "name_km": comm_obj["name_km"] if comm_obj else None,
                "name_en": comm_obj["name_en"] if comm_obj else None,
                "score": comm_score,
            }
            if comm_obj
            else None,
            "village": {
                "code": vill_obj["code"] if vill_obj else None,
                "name_km": vill_obj["name_km"] if vill_obj else None,
                "name_en": vill_obj["name_en"] if vill_obj else None,
                "score": vill_score,
            }
            if vill_obj
            else None,
            "standardized_address_km": std_km,
            "standardized_address_en": std_en,
            "auto_corrected": auto_corrected,
            "discrepancy_alerts": alerts,
        }


# Singleton service instance
cambodia_geo_service = CambodiaGeoService()
