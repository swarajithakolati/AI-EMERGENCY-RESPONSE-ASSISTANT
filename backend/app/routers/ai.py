from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.incident import Incident
from app.schemas.ai import AIAssistantQuery, AIAssistantResponse, AIMatchCheckRequest, AIMatchCheckResponse
from app.engine.understand import understand_report
from app.engine.extract import extract_entities
from app.engine.location_parser import parse_location_intelligence
from app.engine.matcher import match_report_to_incidents
from app.engine.assistant import answer_responder_query

router = APIRouter(prefix="/api/ai", tags=["AI Intelligence"])

@router.post("/analyze", response_model=dict)
def analyze_text(payload: dict):
    """Direct testing endpoint for raw text NLP analysis."""
    text = payload.get("raw_text", "")
    if not text.strip():
        raise HTTPException(status_code=400, detail="raw_text is required.")
    
    understanding = understand_report(text)
    entities = extract_entities(text)
    location = parse_location_intelligence(text)

    return {
        "understanding": understanding,
        "extracted_entities": entities,
        "location_intelligence": location
    }

@router.post("/match", response_model=AIMatchCheckResponse)
def simulate_match(payload: AIMatchCheckRequest, db: Session = Depends(get_db)):
    """Simulates multi-factor duplicate/incident matching for a hypothetical incoming report."""
    understanding = understand_report(payload.raw_text)
    entities = extract_entities(payload.raw_text)
    loc_intel = parse_location_intelligence(payload.raw_text)

    extracted_dict = {
        "emergency_type": understanding["emergency_type"],
        "location_interpreted": loc_intel["location_interpreted"],
        "landmark": loc_intel["landmark"],
        "latitude": loc_intel["latitude"],
        "longitude": loc_intel["longitude"]
    }

    incidents = db.query(Incident).all()
    inc_data = [{
        "id": i.id, "title": i.title, "emergency_type": i.emergency_type,
        "severity": i.severity, "status": i.status,
        "interpreted_location": i.interpreted_location or i.location_name,
        "landmark": i.landmark, "latitude": i.latitude, "longitude": i.longitude
    } for i in incidents]

    eval_res = match_report_to_incidents(extracted_dict, payload.raw_text, inc_data)
    metrics = eval_res.get("metrics", {})

    return AIMatchCheckResponse(
        matched_incident_id=eval_res.get("matched_incident_id"),
        similarity_score=eval_res.get("match_confidence", 0.0),
        location_match=metrics.get("location_reason", "No location match"),
        type_match=f"Score: {metrics.get('type_compatibility', 0.0)}",
        semantic_match=f"Score: {metrics.get('semantic_similarity', 0.0)}",
        time_proximity=f"Score: {metrics.get('time_proximity', 0.0)}",
        decision=eval_res.get("decision", "SEPARATE"),
        reason=eval_res.get("reason", "")
    )

@router.post("/query", response_model=AIAssistantResponse)
async def query_ai_assistant(payload: AIAssistantQuery, db: Session = Depends(get_db)):
    """Natural language AI Responder Assistant answering questions grounded in live incident database."""
    res = await answer_responder_query(payload.query, db, incident_id=payload.incident_id)
    return AIAssistantResponse(
        answer=res["answer"],
        sources_used=res.get("sources_used", []),
        suggested_actions=res.get("suggested_actions", []),
        confidence=res.get("confidence", 0.92)
    )
