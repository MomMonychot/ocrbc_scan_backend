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

        for prov in raw.get("provinces", []):
            prov_entry = {
                "code": prov["code"],
                "name_km": prov["name_km"],
                "name_en": prov["name_en"],
                "type": prov.get("type", "Province"),
            }
            self.provinces.append(prov_entry)
            self._prov_km_list.append(prov["name_km"])

            for dist in prov.get("districts", []):
                dist_entry = {
                    "code": dist["code"],
                    "name_km": dist["name_km"],
                    "name_en": dist["name_en"],
                    "province_code": prov["code"],
                    "province_name_km": prov["name_km"],
                    "province_name_en": prov["name_en"],
                }
                self.districts.append(dist_entry)
                self._dist_km_list.append(dist["name_km"])

                for comm in dist.get("communes", []):
                    comm_entry = {
                        "code": comm["code"],
                        "name_km": comm["name_km"],
                        "name_en": comm["name_en"],
                        "district_code": dist["code"],
                        "district_name_km": dist["name_km"],
                        "province_code": prov["code"],
                        "province_name_km": prov["name_km"],
                    }
                    self.communes.append(comm_entry)
                    self._comm_km_list.append(comm["name_km"])

                    for vill in comm.get("villages", []):
                        vill_entry = {
                            "code": vill["code"],
                            "name_km": vill["name_km"],
                            "name_en": vill["name_en"],
                            "commune_code": comm["code"],
                            "commune_name_km": comm["name_km"],
                            "district_code": dist["code"],
                            "province_code": prov["code"],
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
