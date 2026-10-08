import re
from typing import Dict, Any, Tuple, Optional

KNOWN_LOCATIONS = {
    "velachery mrts": {
        "canonical": "Velachery MRTS Station",
        "lat": 12.9796, "lon": 80.2185,
        "aliases": ["velachery mrts", "mrts station", "mrts", "velachery station", "vijayanagar side", "station backside"],
        "landmarks": ["MRTS Station", "West Gate", "Vijayanagar Side", "Station Backside Road", "MRTS Parking", "Vijayanagar"],
        "zone": "South Chennai",
        "default_radius": 250
    },
    "velachery": {
        "canonical": "Velachery Central",
        "lat": 12.9750, "lon": 80.2200,
        "aliases": ["velachery", "100 feet road", "velachery lake"],
        "landmarks": ["Vijayanagar Bus Terminus", "Grand Square", "Velachery Lake", "100 Feet Road", "MRTS"],
        "zone": "South Chennai",
        "default_radius": 500
    },
    "tambaram": {
        "canonical": "Tambaram Railway Hub",
        "lat": 12.9249, "lon": 80.1000,
        "aliases": ["tambaram", "tambaram sanatorium", "sanatorium", "hindu mission hospital"],
        "landmarks": ["Sanatorium", "Bus Stand", "GST Road", "Railway Station", "Hindu Mission Hospital"],
        "zone": "South West",
        "default_radius": 400
    },
    "guindy": {
        "canonical": "Guindy Industrial Estate & Junction",
        "lat": 13.0067, "lon": 80.2025,
        "aliases": ["guindy", "kathipara", "kathipara junction", "olympia tech park"],
        "landmarks": ["Kathipara Junction", "Guindy Metro", "Olympia Tech Park", "Race Course"],
        "zone": "Central South",
        "default_radius": 350
    },
    "t nagar": {
        "canonical": "T. Nagar Commercial Hub",
        "lat": 13.0418, "lon": 80.2341,
        "aliases": ["t nagar", "t. nagar", "t.nagar", "usman road", "panagal park", "ranganathan street"],
        "landmarks": ["Usman Road", "Ranganathan Street", "Panagal Park", "South Usman Flyover"],
        "zone": "Central Chennai",
        "default_radius": 300
    },
    "omr": {
        "canonical": "OMR IT Corridor",
        "lat": 12.9345, "lon": 80.2312,
        "aliases": ["omr", "karapakkam", "sholinganallur", "perungudi toll", "thoraipakkam"],
        "landmarks": ["Karapakkam", "Sholinganallur Junction", "Perungudi Toll", "Thoraipakkam"],
        "zone": "IT Corridor",
        "default_radius": 800
    },
    "adyar": {
        "canonical": "Adyar Basin",
        "lat": 13.0012, "lon": 80.2565,
        "aliases": ["adyar", "gandhi nagar", "adyar bridge", "kotturpuram"],
        "landmarks": ["Adyar Bridge", "Malarm Hospital", "Gandhi Nagar", "Kotturpuram Riverbank"],
        "zone": "South Coast",
        "default_radius": 350
    },
    "koyambedu": {
        "canonical": "Koyambedu Hub",
        "lat": 13.0694, "lon": 80.1948,
        "aliases": ["koyambedu", "cmbt", "koyambedu market", "poonamallee high rd"],
        "landmarks": ["Koyambedu Wholesale Market", "CMBT Bus Terminal", "Metro Depot", "Poonamallee High Rd"],
        "zone": "West Central",
        "default_radius": 400
    },
    "madipakkam": {
        "canonical": "Madipakkam Lowlands",
        "lat": 12.9647, "lon": 80.1961,
        "aliases": ["madipakkam", "kuberan nagar", "balaiah nagar", "madipakkam lake"],
        "landmarks": ["Madipakkam Lake", "Kuberan Nagar", "Puzhuthivakkam Main Rd", "Balaiah Nagar"],
        "zone": "South Chennai",
        "default_radius": 450
    },
    "perumbakkam": {
        "canonical": "Perumbakkam Resettlement",
        "lat": 12.8988, "lon": 80.1983,
        "aliases": ["perumbakkam", "global hospital"],
        "landmarks": ["Global Hospital", "Perumbakkam Lake", "Housing Board Blocks"],
        "zone": "South Periphery",
        "default_radius": 500
    },
    "medavakkam": {
        "canonical": "Medavakkam Junction",
        "lat": 12.9181, "lon": 80.1912,
        "aliases": ["medavakkam", "nanmangalam"],
        "landmarks": ["Medavakkam Flyover", "Nanmangalam Reserve", "Tambaram-Velachery Main Rd"],
        "zone": "South",
        "default_radius": 400
    },
    "saidapet": {
        "canonical": "Saidapet Adyar Crossing",
        "lat": 13.0210, "lon": 80.2231,
        "aliases": ["saidapet", "saidapet bridge", "saidapet bazaar road"],
        "landmarks": ["Saidapet Bridge", "Saidapet Metro", "Court Complex", "Bazaar Road"],
        "zone": "Central South",
        "default_radius": 350
    },
    "mudichur": {
        "canonical": "Mudichur Flood Plain",
        "lat": 12.9056, "lon": 80.0708,
        "aliases": ["mudichur", "varadharajapuram"],
        "landmarks": ["Mudichur Road", "Varadharajapuram", "Adyar River Source"],
        "zone": "South West Basin",
        "default_radius": 600
    }
}

DIRECTIONS = ["west gate", "east gate", "north gate", "south gate", "backside road", "backside", "opposite", "behind", "near", "junction", "inside", "under", "flyover", "station"]

def parse_location_intelligence(text: str) -> Dict[str, Any]:
    """
    Extracts raw location, interpreted location, specific landmark,
    best-known location, and honest confidence score without false precision.
    """
    cleaned = text.lower()
    
    # 1. Match against known locations and aliases
    detected_key = None
    best_match_len = 0
    
    for key, data in KNOWN_LOCATIONS.items():
        for alias in data.get("aliases", [key]):
            if alias in cleaned:
                if len(alias) > best_match_len:
                    best_match_len = len(alias)
                    detected_key = key

    # Check for relative location phrases
    loc_phrase = ""
    landmark_detail = ""
    
    loc_regexes = [
        r"(?:near|at|around|behind|opposite|beside|under|inside|next to)\s+([a-zA-Z0-9\s,\-\.]{3,40}?)(?:\.|\band\b|\bwith\b|\bwater\b|\bpeople\b|\bfire\b|\bhelp\b|\bnow\b|$)",
        r"([a-zA-Z0-9\s,\-\.]{3,30}?\s+(?:mrts|station|junction|bridge|lake|flyover|market|hospital|road|street|gate|apartment|school))"
    ]
    
    for rgx in loc_regexes:
        match = re.search(rgx, cleaned, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if len(candidate) > 2 and not candidate.startswith("6") and not candidate.startswith("10"):
                loc_phrase = candidate
                break

    for direction in DIRECTIONS:
        if direction in cleaned:
            landmark_detail = direction.title()
            break

    if detected_key:
        loc_data = KNOWN_LOCATIONS[detected_key]
        canonical = loc_data["canonical"]
        
        found_landmark = None
        for lm in loc_data["landmarks"]:
            if lm.lower() in cleaned:
                found_landmark = lm
                break
        
        if not found_landmark and landmark_detail:
            found_landmark = landmark_detail
            
        best_known = canonical
        if found_landmark:
            best_known = f"{canonical} — {found_landmark}"
            confidence = 0.88
            uncertainty_radius = 180.0
        else:
            confidence = 0.78
            uncertainty_radius = loc_data["default_radius"]

        return {
            "location_raw": loc_phrase if loc_phrase else detected_key.title(),
            "location_interpreted": canonical,
            "landmark": found_landmark or (loc_data["landmarks"][0] if loc_data["landmarks"] else None),
            "best_known_location": best_known,
            "location_confidence": round(confidence, 2),
            "latitude": loc_data["lat"],
            "longitude": loc_data["lon"],
            "uncertainty_radius_m": uncertainty_radius,
            "reason": f"Matched landmark '{detected_key.title()}' with surrounding context clues."
        }

    elif loc_phrase:
        title_case_loc = loc_phrase.title()
        return {
            "location_raw": loc_phrase,
            "location_interpreted": title_case_loc,
            "landmark": landmark_detail if landmark_detail else "General Area",
            "best_known_location": f"{title_case_loc} (Approximate Area)",
            "location_confidence": 0.45,
            "latitude": 12.9716,
            "longitude": 80.2206,
            "uncertainty_radius_m": 800.0,
            "reason": "Descriptive location extracted from text; exact coordinates pending field verification."
        }
    else:
        return {
            "location_raw": "Not specified in report",
            "location_interpreted": "Unknown Location",
            "landmark": None,
            "best_known_location": "Location Pending Verification",
            "location_confidence": 0.20,
            "latitude": 12.9716,
            "longitude": 80.2206,
            "uncertainty_radius_m": 1500.0,
            "reason": "No geographic references detected in incoming text."
        }
