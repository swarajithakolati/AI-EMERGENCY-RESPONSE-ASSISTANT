import math
import re
from typing import List, Dict, Any, Tuple, Optional

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates distance in kilometers between two GPS coordinates."""
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

CONTEXTUAL_ANAPHORA_PATTERNS = [
    r"\bsame (?:place|location|building|house|gate|area|spot|site)\b",
    r"\b(?:right )?here\b",
    r"\bfrom here\b",
    r"\bstill inside\b",
    r"\binside the (?:house|building|station|shop)\b",
    r"\bat this (?:location|place|spot)\b",
    r"\bon site\b"
]

def compute_location_similarity(loc1: Dict[str, Any], loc2: Dict[str, Any], raw_text: str, total_active_incidents: int = 1) -> Tuple[float, str]:
    """Computes similarity between incoming report location and existing incident location."""
    raw_lower = raw_text.lower()
    
    # 1. Check for strong contextual anaphora / references
    for pat in CONTEXTUAL_ANAPHORA_PATTERNS:
        if re.search(pat, raw_lower):
            return 0.96, f"Contextual reference matching active incident ('{pat.replace(chr(92), '')}')"

    name1 = (loc1.get("interpreted_location") or "").lower()
    name2 = (loc2.get("interpreted_location") or "").lower()
    
    lm1 = (loc1.get("landmark") or "").lower()
    lm2 = (loc2.get("landmark") or "").lower()

    # Exact canonical location match (e.g. Velachery MRTS Station == Velachery MRTS Station)
    if name1 and name2 and name1 == name2:
        if lm1 and lm2 and (lm1 in lm2 or lm2 in lm1):
            return 0.98, f"Exact landmark and zone match: '{lm1}'"
        return 0.90, f"Same geographic zone: '{name1}'"

    # Haversine distance if lat/lon present
    lat1, lon1 = loc1.get("latitude"), loc1.get("longitude")
    lat2, lon2 = loc2.get("latitude"), loc2.get("longitude")
    
    if lat1 and lon1 and lat2 and lon2:
        dist_km = calculate_haversine_distance(lat1, lon1, lat2, lon2)
        if dist_km <= 0.40: # within 400 meters
            return 0.94, f"Geographic proximity within {int(dist_km * 1000)}m"
        elif dist_km <= 0.85: # within 850 meters
            return 0.78, f"Geographic proximity within {int(dist_km * 1000)}m"
        elif dist_km <= 2.0:
            return 0.45, f"Nearby sector ({dist_km:.1f} km)"
        else:
            return 0.10, f"Distant location ({dist_km:.1f} km away)"

    # Substring / partial match on name or landmark
    if name1 and name2:
        if name1 in name2 or name2 in name1:
            return 0.82, f"Partial location name overlap: '{name1}' / '{name2}'"
    
    if lm1 and lm2:
        if lm1 in lm2 or lm2 in lm1:
            return 0.88, f"Landmark correlation: '{lm1}'"

    # If no location specified at all in follow-up report and only 1 active incident exists
    if loc1.get("location_interpreted") == "Unknown Location" and total_active_incidents == 1:
        return 0.85, "Follow-up update with implicit location correlated to sole active incident"

    return 0.20, "No strong location overlap detected"

def compute_type_compatibility(type1: str, type2: str) -> float:
    """Computes compatibility between emergency types."""
    t1 = type1.lower()
    t2 = type2.lower()
    
    if t1 == t2:
        return 1.0
        
    compatibles = [
        {"flood", "rescue"},
        {"fire", "rescue"},
        {"building collapse", "rescue"},
        {"accident", "medical"},
        {"medical", "rescue"},
        {"flood", "medical"},
        {"other", "flood"},
        {"other", "rescue"}
    ]
    for pair in compatibles:
        if t1 in pair and t2 in pair:
            return 0.88
            
    if t1 == "other" or t2 == "other":
        return 0.70
        
    return 0.25

def match_report_to_incidents(
    extracted_report: Dict[str, Any],
    raw_text: str,
    active_incidents: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Finds best matching existing incident for an incoming report.
    Returns match evaluation with scores, decision, and reasons.
    """
    if not active_incidents:
        return {
            "matched_incident_id": None,
            "match_confidence": 0.0,
            "decision": "SEPARATE",
            "reason": "No active incidents currently open in the system.",
            "metrics": {}
        }

    best_incident = None
    best_score = 0.0
    best_metrics = {}

    rep_loc = {
        "interpreted_location": extracted_report.get("location_interpreted"),
        "landmark": extracted_report.get("landmark"),
        "latitude": extracted_report.get("latitude"),
        "longitude": extracted_report.get("longitude")
    }
    rep_type = extracted_report.get("emergency_type", "Other")

    for inc in active_incidents:
        is_resolved = inc.get("status") == "RESOLVED"
        
        inc_loc = {
            "interpreted_location": inc.get("interpreted_location") or inc.get("location_name"),
            "landmark": inc.get("landmark"),
            "latitude": inc.get("latitude"),
            "longitude": inc.get("longitude")
        }
        inc_type = inc.get("emergency_type", "Other")

        # 1. Location similarity
        loc_score, loc_reason = compute_location_similarity(rep_loc, inc_loc, raw_text, total_active_incidents=len(active_incidents))

        # 2. Type compatibility
        type_score = compute_type_compatibility(rep_type, inc_type)

        # 3. Semantic similarity
        semantic_score = 0.70
        raw_lower = raw_text.lower()
        if any(term in raw_lower for term in ["water", "trapped", "elderly", "rescue", "fire", "people", "doctor", "insulin", "boat"]):
            semantic_score = 0.90

        # 4. Time proximity
        time_score = 0.90

        # Weighted aggregate
        overall = (0.50 * loc_score) + (0.25 * type_score) + (0.15 * semantic_score) + (0.10 * time_score)

        if is_resolved and not any(k in raw_lower for k in ["everyone rescued", "all safe", "resolved", "cleared"]):
            overall *= 0.40 # Penalize reopening resolved incident with standard duplicates

        if overall > best_score:
            best_score = overall
            best_incident = inc
            best_metrics = {
                "location_similarity": round(loc_score, 2),
                "type_compatibility": round(type_score, 2),
                "semantic_similarity": round(semantic_score, 2),
                "time_proximity": round(time_score, 2),
                "location_reason": loc_reason,
                "incident_id": inc.get("id"),
                "incident_title": inc.get("title")
            }

    if best_score >= 0.75 and best_incident:
        decision = "AUTO_MERGE"
        reason = f"High confidence match ({int(best_score*100)}%) with {best_incident.get('id')}: {best_metrics.get('location_reason')}"
    elif best_score >= 0.45 and best_incident:
        decision = "REVIEW_NEEDED"
        reason = f"Moderate similarity ({int(best_score*100)}%) with {best_incident.get('id')}. Human dispatcher review recommended."
    else:
        decision = "SEPARATE"
        reason = "Report does not match existing active incidents; creating a new evolving incident record."

    return {
        "matched_incident_id": best_incident.get("id") if (decision in ["AUTO_MERGE", "REVIEW_NEEDED"] and best_incident) else None,
        "match_confidence": round(best_score, 2),
        "decision": decision,
        "reason": reason,
        "metrics": best_metrics
    }
