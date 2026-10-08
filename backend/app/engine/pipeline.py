import datetime
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.report import RawReport
from app.models.incident import Incident, IncidentUpdate
from app.models.audit import AuditLog
from app.engine.understand import understand_report
from app.engine.extract import extract_entities
from app.engine.location_parser import parse_location_intelligence
from app.engine.matcher import match_report_to_incidents
from app.engine.tracker import apply_report_to_incident

def generate_report_id(db: Session) -> str:
    count = db.query(RawReport).count() + 1
    return f"REP-{1000 + count}"

def generate_incident_id(db: Session) -> str:
    count = db.query(Incident).count() + 1
    return f"INC-{1000 + count}"

def process_incoming_report(
    raw_text: str,
    source: str,
    db: Session,
    custom_timestamp: Optional[datetime.datetime] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Executes the 5-Part Mandatory Flow:
    1. INGEST
    2. UNDERSTAND
    3. EXTRACT
    4. TRACK
    5. SHOW
    """
    # --------------------------------
    # 1. INGEST
    # --------------------------------
    rep_id = generate_report_id(db)
    now = custom_timestamp or datetime.datetime.utcnow()
    
    report = RawReport(
        id=rep_id,
        source=source.upper(),
        timestamp=now,
        raw_text=raw_text.strip(),
        processing_status="RECEIVED",
        metadata_json=metadata or {}
    )
    db.add(report)
    db.flush()

    # --------------------------------
    # 2. UNDERSTAND
    # --------------------------------
    report.processing_status = "ANALYZING"
    db.flush()

    understanding = understand_report(raw_text)
    report.is_emergency = understanding["is_emergency"]
    report.is_relevant = understanding["is_relevant"]
    report.is_noise = understanding["is_noise"]
    report.is_rumor = understanding["is_rumor"]
    report.emergency_type = understanding["emergency_type"]
    report.urgency = understanding["urgency"]
    report.verification = understanding["verification"]
    report.processing_status = "UNDERSTOOD"
    db.flush()

    # If classified as noise/non-emergency, archive without creating incident
    if report.is_noise or not report.is_emergency:
        report.processing_status = "NOISE"
        audit = AuditLog(
            action="REPORT_FILTERED_NOISE",
            actor="AI",
            source=report.source,
            report_id=report.id,
            previous_state="UNPROCESSED",
            new_state="NOISE_FILTERED",
            notes=f"Filtered non-emergency query: '{raw_text[:60]}...'"
        )
        db.add(audit)
        db.commit()
        db.refresh(report)
        return {
            "flow_stage": "SHOW",
            "status": "FILTERED_NOISE",
            "report": report,
            "incident": None,
            "message": "Report classified as non-emergency/noise. Saved to audit history without creating incident."
        }

    # --------------------------------
    # 3. EXTRACT
    # --------------------------------
    report.processing_status = "EXTRACTING"
    entities = extract_entities(raw_text)
    loc_intel = parse_location_intelligence(raw_text)

    # Merge extracted details
    report.location_raw = loc_intel["location_raw"]
    report.location_interpreted = loc_intel["location_interpreted"]
    report.landmark = loc_intel["landmark"]
    report.people_affected = str(entities["people_affected"]) if entities["people_affected"] is not None else None
    report.vulnerable_people = entities["vulnerable_people"]
    report.resource_needed = entities["resource_needed"]
    report.status_signal = entities["status_signal"]
    report.evidence = understanding.get("evidence")
    report.confidence = round((understanding.get("confidence", 0.75) + entities["confidence"] + loc_intel["location_confidence"]) / 3.0, 2)
    report.processing_status = "EXTRACTED"
    db.flush()

    extracted_dict = {
        "emergency_type": report.emergency_type,
        "urgency": report.urgency,
        "location_interpreted": loc_intel["location_interpreted"],
        "landmark": loc_intel["landmark"],
        "best_known_location": loc_intel["best_known_location"],
        "latitude": loc_intel["latitude"],
        "longitude": loc_intel["longitude"],
        "location_confidence": loc_intel["location_confidence"],
        "people_affected": entities["people_affected"],
        "vulnerable_people": entities["vulnerable_people"],
        "resource_needed": entities["resource_needed"],
        "status_signal": entities["status_signal"]
    }

    # --------------------------------
    # 4. TRACK
    # --------------------------------
    report.processing_status = "MATCHING"
    
    # Query all active or recent incidents
    active_incidents = db.query(Incident).all()
    incidents_data = []
    for inc in active_incidents:
        incidents_data.append({
            "id": inc.id,
            "title": inc.title,
            "emergency_type": inc.emergency_type,
            "severity": inc.severity,
            "status": inc.status,
            "location_name": inc.location_name,
            "interpreted_location": inc.interpreted_location,
            "landmark": inc.landmark,
            "latitude": inc.latitude,
            "longitude": inc.longitude
        })

    match_eval = match_report_to_incidents(extracted_dict, raw_text, incidents_data)
    decision = match_eval["decision"]
    matched_id = match_eval.get("matched_incident_id")
    match_conf = match_eval.get("match_confidence", 0.0)

    report.match_confidence = match_conf
    report.match_reason = match_eval.get("reason")
    report.match_status = decision

    target_incident = None

    if decision == "AUTO_MERGE" and matched_id:
        target_incident = db.query(Incident).filter(Incident.id == matched_id).first()
        if target_incident:
            report.matched_incident_id = target_incident.id
            report.processing_status = "UPDATED"
            apply_report_to_incident(db, target_incident, report, extracted_dict, actor="AI")
    
    elif decision == "REVIEW_NEEDED" and matched_id:
        # Flag for human review - do not silently merge
        report.matched_incident_id = matched_id
        report.processing_status = "FLAGGED"
        report.verification = "Unverified"
        audit = AuditLog(
            action="MATCH_REVIEW_FLAGGED",
            actor="AI",
            source=report.source,
            incident_id=matched_id,
            report_id=report.id,
            previous_state="PENDING_MATCH",
            new_state="PENDING_HUMAN_REVIEW",
            notes=f"Possible match with {matched_id} (confidence: {int(match_conf*100)}%). Awaiting dispatcher verification."
        )
        db.add(audit)
        target_incident = db.query(Incident).filter(Incident.id == matched_id).first()

    else:
        # Decision is SEPARATE -> create new evolving incident
        inc_id = generate_incident_id(db)
        
        init_severity = report.urgency
        init_people = entities["people_affected"] or 0
        init_title = f"{report.emergency_type} at {loc_intel['best_known_location']}"
        init_summary = f"{report.emergency_type} reported at {loc_intel['best_known_location']}. {entities['people_affected'] or 'Unspecified number of'} people affected. Initial resource: {entities['resource_needed']}."

        target_incident = Incident(
            id=inc_id,
            title=init_title,
            emergency_type=report.emergency_type,
            severity=init_severity,
            status="ACTIVE",
            verification="Unverified" if report.is_rumor else "Partially Verified",
            primary_resource=entities["resource_needed"] or "Rescue team",
            people_affected=init_people,
            vulnerable_people=entities["vulnerable_people"],
            location_name=loc_intel["location_raw"],
            interpreted_location=loc_intel["location_interpreted"],
            landmark=loc_intel["landmark"],
            best_known_location=loc_intel["best_known_location"],
            location_confidence=loc_intel["location_confidence"],
            latitude=loc_intel["latitude"],
            longitude=loc_intel["longitude"],
            uncertainty_radius_m=loc_intel["uncertainty_radius_m"],
            summary=init_summary,
            confidence=report.confidence,
            report_count=1
        )
        db.add(target_incident)
        db.flush()

        report.matched_incident_id = target_incident.id
        report.processing_status = "MATCHED"

        # Create Initial Incident Update
        init_update = IncidentUpdate(
            incident_id=target_incident.id,
            update_type="CREATED",
            description=f"Incident established from initial {report.source} report.",
            actor="AI",
            source_report_id=report.id,
            evidence=raw_text,
            previous_state={},
            new_state={
                "severity": target_incident.severity,
                "status": target_incident.status,
                "people_affected": target_incident.people_affected,
                "best_known_location": target_incident.best_known_location
            }
        )
        db.add(init_update)

        audit = AuditLog(
            action="INCIDENT_CREATED",
            actor="AI",
            source=report.source,
            incident_id=target_incident.id,
            report_id=report.id,
            previous_state="NONE",
            new_state=str({"id": target_incident.id, "title": target_incident.title, "severity": target_incident.severity}),
            notes=f"Created new incident record '{target_incident.id}'"
        )
        db.add(audit)

    db.commit()
    db.refresh(report)
    if target_incident:
        db.refresh(target_incident)

    # --------------------------------
    # 5. SHOW
    # --------------------------------
    return {
        "flow_stage": "SHOW",
        "status": "SUCCESS",
        "report": report,
        "incident": target_incident,
        "match_decision": decision,
        "match_confidence": match_conf,
        "extracted_entities": extracted_dict,
        "message": f"Report processed. Incident {target_incident.id if target_incident else 'N/A'} active."
    }
