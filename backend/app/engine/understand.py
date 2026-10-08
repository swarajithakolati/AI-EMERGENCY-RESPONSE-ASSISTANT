import re
from typing import Dict, Any

# Clear noise / non-emergency patterns
NOISE_PATTERNS = [
    r"\btraffic\b.*\b(near|at|on|in|clear|jam|slow|moving)\b",
    r"\bis there traffic\b",
    r"\bwill it rain\b",
    r"\bweather (forecast|tomorrow|update|report)\b",
    r"\bpower cut\b.*\b(street|house|area|normal|scheduled)\b",
    r"\bwhere can i order food\b",
    r"\bis (swiggy|zomato|uber|ola) working\b",
    r"\bany hotel open\b",
    r"\bis school open\b",
    r"\bis holiday announced\b",
    r"\bwhere to buy (groceries|milk|vegetables)\b",
    r"\bjust checking in\b",
    r"\bcan someone tell me if rain stopped\b",
    r"\bhow is the road condition\b"
]

# Emergency Type keyword indicators
EMERGENCY_TYPES = {
    "Flood": [
        "water rising", "water level", "submerged", "flooding", "flood", "inundated",
        "chest deep", "knee deep", "water entered", "lake breached", "overflowing", "stranded in water", "boat needed"
    ],
    "Fire": [
        "fire", "flames", "smoke", "burning", "short circuit fire", "cylinder explosion", "blaze", "fire engine needed"
    ],
    "Medical": [
        "heart attack", "unconscious", "bleeding", "pregnant", "labor pain", "diabetic", "insulin", "oxygen",
        "dialysis", "ambulance needed", "paramedic", "cpr", "critical condition", "choking", "seizure"
    ],
    "Rescue": [
        "trapped", "stranded", "stuck", "roof", "terrace", "cannot get out", "marooned", "evacuate",
        "save us", "help us out", "ndrf", "rescue team"
    ],
    "Building collapse": [
        "collapse", "building fell", "wall collapsed", "roof fell", "debris", "rubble", "crushed"
    ],
    "Accident": [
        "accident", "bus hit", "car crash", "collision", "overturned", "capsized", "hit and run"
    ],
    "Missing person": [
        "missing", "lost child", "swept away", "cannot find", "separated", "whereabouts unknown"
    ],
    "Road blockage": [
        "tree fallen", "pole fallen", "road blocked", "road cut off", "bridge damaged", "traffic completely stopped due to fallen tree"
    ],
    "Power emergency": [
        "live wire", "transformer blast", "electric shock", "hanging live cable", "electrocution risk"
    ]
}

# Urgency indicators
CRITICAL_SIGNALS = [
    "critical", "dying", "oxygen running out", "cannot breathe", "infant", "newborn",
    "unconscious", "chest pain", "bleeding profusely", "fire spreading fast",
    "water reached 2nd floor", "roof collapsing", "submerged completely", "insulin emergency", "drowning"
]

HIGH_SIGNALS = [
    "trapped", "water rising", "elderly", "children", "pregnant", "no food or water for 24h",
    "smoke inhalation", "electric shock risk", "rising fast", "stranded on terrace", "urgent"
]

LOW_SIGNALS = [
    "water logging 1 foot", "minor tree branch", "pothole", "water drained", "no life threat"
]

# Rumor / Sensationalist patterns for verification flagging
RUMOR_PATTERNS = [
    r"\bheard that\b",
    r"\bsomeone said\b",
    r"\bunconfirmed rumor\b",
    r"\bforwarded as received\b",
    r"\bis it true that\b",
    r"\bwhatsapp forward says\b",
    r"\bapparently\b"
]

def understand_report(text: str) -> Dict[str, Any]:
    """
    Analyzes incoming raw text to classify:
    - is_emergency vs noise
    - emergency_type
    - urgency (Critical, High, Medium, Low)
    - is_rumor / verification state
    """
    cleaned = text.strip()
    lower_text = cleaned.lower()

    # 1. Check for non-emergency noise
    is_noise = False
    for pat in NOISE_PATTERNS:
        if re.search(pat, lower_text):
            # Check if there is an explicit life-safety distress override
            if not any(k in lower_text for k in ["trapped", "save", "urgent", "help", "emergency", "fire", "bleeding"]):
                is_noise = True
                break

    if is_noise:
        return {
            "is_emergency": False,
            "is_relevant": False,
            "is_noise": True,
            "is_rumor": False,
            "emergency_type": "None",
            "urgency": "Low",
            "verification": "Unknown",
            "evidence": "Classified as non-emergency informational inquiry or traffic query."
        }

    # 2. Emergency Type Classification
    detected_type = "Other"
    best_score = 0
    for em_type, keywords in EMERGENCY_TYPES.items():
        score = sum(1 for kw in keywords if kw in lower_text)
        if score > best_score:
            best_score = score
            detected_type = em_type

    # Default to Rescue if trapped mentioned
    if detected_type == "Other" and ("trapped" in lower_text or "help" in lower_text or "save" in lower_text):
        detected_type = "Rescue"

    # 3. Urgency Scoring
    urgency = "Medium"
    if any(sig in lower_text for sig in CRITICAL_SIGNALS):
        urgency = "Critical"
    elif any(sig in lower_text for sig in HIGH_SIGNALS) or "trapped" in lower_text or "flood" in lower_text:
        urgency = "High"
    elif any(sig in lower_text for sig in LOW_SIGNALS):
        urgency = "Low"

    # 4. Rumor and Verification Detection
    is_rumor = False
    for rpat in RUMOR_PATTERNS:
        if re.search(rpat, lower_text):
            is_rumor = True
            break

    verification = "Unverified"
    if is_rumor:
        verification = "Unverified"
    elif "police verified" in lower_text or "fire officer on site" in lower_text or "rescue team reached" in lower_text:
        verification = "Verified"

    return {
        "is_emergency": True,
        "is_relevant": True,
        "is_noise": False,
        "is_rumor": is_rumor,
        "emergency_type": detected_type,
        "urgency": urgency,
        "verification": verification,
        "evidence": f"Identified as {urgency} {detected_type} emergency."
    }
