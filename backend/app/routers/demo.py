import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.incident import Incident, IncidentUpdate
from app.models.report import RawReport
from app.seed.seed_data import seed_database
from app.engine.pipeline import process_incoming_report

router = APIRouter(prefix="/api/demo", tags=["Live Demo & Showcase"])

DEMO_STAGES = [
    {
        "stage": 1,
        "title": "Stage 1: Initial Inundation Report",
        "raw_text": "6 people trapped near Velachery MRTS.",
        "source": "WHATSAPP",
        "expected_action": "System creates new incident: Flood at Velachery MRTS (6 people affected)."
    },
    {
        "stage": 2,
        "title": "Stage 2: Duplicate Recognition & Count Update",
        "raw_text": "Same place, water has increased. 10 people now.",
        "source": "SMS",
        "expected_action": "Recognizes same incident via landmark/context ('Same place'). Updates people count: 6 → 10."
    },
    {
        "stage": 3,
        "title": "Stage 3: Vulnerability & Medical Need Detection",
        "raw_text": "Elderly person is still inside and needs insulin.",
        "source": "AUDIO",
        "expected_action": "Detects vulnerable person (Elderly diabetic). Escalates urgency to Critical. Requests Medical Ambulance."
    },
    {
        "stage": 4,
        "title": "Stage 4: Environmental Escalation Signal",
        "raw_text": "Water is rising fast near the gate.",
        "source": "SOCIAL_MEDIA",
        "expected_action": "Detects rapid hazard escalation. Sets status to ESCALATED with clear causal evidence."
    },
    {
        "stage": 5,
        "title": "Stage 5: Field Team Arrival",
        "raw_text": "Rescue team has reached on site with inflatable boats.",
        "source": "MANUAL",
        "expected_action": "Detects operational status change. Transitions incident status to RESCUE IN PROGRESS."
    },
    {
        "stage": 6,
        "title": "Stage 6: Successful Incident Resolution",
        "raw_text": "Everyone rescued safely. Area secured.",
        "source": "AUDIO",
        "expected_action": "Detects mission completion. Transitions incident status to RESOLVED."
    }
]

@router.get("/stages")
def get_demo_stages():
    """Returns metadata for the 6-stage Velachery showcase pipeline."""
    return DEMO_STAGES

@router.post("/reset")
def reset_demo_database(db: Session = Depends(get_db)):
    """Resets the entire database and seeds 20+ incidents and 100+ raw reports."""
    seed_database(db)
    return {"status": "SUCCESS", "message": "Database reset and seeded with 20+ incidents and 100+ reports."}

@router.post("/step/{stage_id}")
def execute_demo_step(stage_id: int, db: Session = Depends(get_db)):
    """Executes a specific step (1-6) of the Velachery MRTS live demonstration."""
    if stage_id < 1 or stage_id > 6:
        raise HTTPException(status_code=400, detail="Stage ID must be between 1 and 6.")

    stage_info = DEMO_STAGES[stage_id - 1]
    
    res = process_incoming_report(
        raw_text=stage_info["raw_text"],
        source=stage_info["source"],
        db=db
    )

    report_obj = res["report"]
    inc_obj = res["incident"]

    return {
        "stage": stage_id,
        "stage_title": stage_info["title"],
        "input_text": stage_info["raw_text"],
        "source": stage_info["source"],
        "expected_action": stage_info["expected_action"],
        "match_decision": res.get("match_decision"),
        "match_confidence": res.get("match_confidence"),
        "report": {
            "id": report_obj.id,
            "processing_status": report_obj.processing_status,
            "emergency_type": report_obj.emergency_type,
            "urgency": report_obj.urgency,
            "matched_incident_id": report_obj.matched_incident_id
        },
        "incident": {
            "id": inc_obj.id,
            "title": inc_obj.title,
            "status": inc_obj.status,
            "severity": inc_obj.severity,
            "people_affected": inc_obj.people_affected,
            "vulnerable_people": inc_obj.vulnerable_people,
            "best_known_location": inc_obj.best_known_location,
            "report_count": inc_obj.report_count,
            "last_escalation_reason": inc_obj.last_escalation_reason
        } if inc_obj else None
    }
