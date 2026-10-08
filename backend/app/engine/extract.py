import re
from typing import Dict, Any, Optional

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30,
    "fifty": 50, "hundred": 100
}

VULNERABILITY_PATTERNS = [
    (r"\b(elderly|senior citizen|old man|old woman|aged person|grandpa|grandma|octogenarian)\b", "Elderly Person"),
    (r"\b(insulin|diabetic|diabetes)\b", "Diabetic / Insulin Needed"),
    (r"\b(pregnant|pregnancy|expecting mother)\b", "Pregnant Woman"),
    (r"\b(infant|baby|newborn|toddler)\b", "Infant / Small Child"),
    (r"\b(child|children|kids)\b", "Children"),
    (r"\b(oxygen|dialysis|ventilator|bedridden|disabled|wheelchair|paralyzed)\b", "Critical Medical Dependency"),
    (r"\b(heart patient|cardiac)\b", "Heart Condition")
]

STATUS_SIGNALS = [
    (r"\b(everyone (?:is |was |has been )?rescued|all (?:are |were |have been )?rescued|safely evacuated|operation completed|all safe|situation under control|all cleared)\b", "RESOLVED"),
    (r"\b(rescue team (?:has )?reached|boats? (?:have )?arrived|fire brigade reached|ndrf arrived|ambulance reached|on site now|rescue underway|rescue in progress)\b", "RESCUE_IN_PROGRESS"),
    (r"\b(water (?:is |has )?rising|water (?:is |has )?increased|flames spreading|fire spreading|structure weakening|worsening|escalating)\b", "ESCALATED"),
    (r"\b(trapped|stuck|stranded|marooned)\b", "ACTIVE")
]

RESOURCE_MAPPINGS = [
    (r"\b(insulin|medical|oxygen|ambulance|paramedic|doctor|hospital|bleeding|chest pain|dialysis)\b", "Medical Support & Ambulance"),
    (r"\b(fire|flames|smoke|explosion|burn)\b", "Fire Response Unit"),
    (r"\b(boat|boats|inflatable|flood|water rising|submerged)\b", "Inflatable Rescue Boats & NDRF"),
    (r"\b(trapped|stranded|terrace|roof|evacuate|rescue team)\b", "Rescue Team & Evacuation Unit"),
    (r"\b(tree fallen|pole fallen|crane|debris|road blocked)\b", "Heavy Road Clearance Crane"),
    (r"\b(food|water packets|air drop|starving)\b", "Emergency Relief Food/Water Supplies")
]

def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extracts structured entities:
    - people_affected count
    - vulnerable_people description
    - resource_needed
    - status_signal
    - confidence
    """
    cleaned = text.lower()
    
    # 1. Extract People Affected Count
    people_count = None
    
    # Check digits + people/persons/trapped
    people_regexes = [
        r"(\d+)\s+(?:people|persons|residents|citizens|members|souls|individuals|victims|trapped|now|inside)",
        r"(?:family of|group of|about|around|only)\s+(\d+)",
        r"(\d+)\s+trapped",
        r"(\d+)\s+now"
    ]
    for rgx in people_regexes:
        m = re.search(rgx, cleaned)
        if m:
            people_count = int(m.group(1))
            break
            
    if people_count is None:
        # Check spelled numbers e.g. "six people", "four trapped"
        for word, val in NUMBER_WORDS.items():
            if re.search(rf"\b{word}\s+(?:people|persons|trapped|now|residents|victims)\b", cleaned):
                people_count = val
                break
                
    # 2. Extract Vulnerable People
    vulnerable_items = []
    for pat, label in VULNERABILITY_PATTERNS:
        if re.search(pat, cleaned):
            vulnerable_items.append(label)
    
    vulnerable_desc = ", ".join(list(dict.fromkeys(vulnerable_items))) if vulnerable_items else None

    # 3. Extract Resource Needed
    resource_needed = "General Rescue Team"
    for pat, resource in RESOURCE_MAPPINGS:
        if re.search(pat, cleaned):
            resource_needed = resource
            break

    # 4. Extract Status Signal
    status_signal = None
    for pat, sig in STATUS_SIGNALS:
        if re.search(pat, cleaned):
            status_signal = sig
            break

    # 5. Extract Confidence
    confidence = 0.75
    if people_count is not None:
        confidence += 0.1
    if vulnerable_desc:
        confidence += 0.05
    if status_signal:
        confidence += 0.05
    confidence = min(0.98, confidence)

    return {
        "people_affected": people_count,
        "vulnerable_people": vulnerable_desc,
        "resource_needed": resource_needed,
        "status_signal": status_signal,
        "confidence": round(confidence, 2)
    }
