import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.incident import Incident, IncidentUpdate, IncidentConflict
from app.models.report import RawReport
from app.models.audit import AuditLog
from app.schemas.incident import (
    IncidentResponse,
    IncidentDetailResponse,
    IncidentManualUpdate,
    IncidentMergeRequest,
    IncidentResolveConflictRequest
)

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentResponse])
def list_incidents(
    emergency_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    verification: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists all evolving incidents with multi-factor filtering and search."""
    query = db.query(Incident)
    
    if emergency_type and emergency_type != "All":
        query = query.filter(Incident.emergency_type == emergency_type)
    if severity and severity != "All":
        query = query.filter(Incident.severity == severity)
    if status and status != "All":
        query = query.filter(Incident.status == status)
    if verification and verification != "All":
        query = query.filter(Incident.verification == verification)
    if search:
        s_term = f"%{search.strip()}%"
        query = query.filter(
            (Incident.title.ilike(s_term)) |
            (Incident.best_known_location.ilike(s_term)) |
            (Incident.summary.ilike(s_term)) |
            (Incident.id.ilike(s_term))
        )

    # Order by severity priority, then updated_at desc
    incidents = query.order_by(Incident.updated_at.desc()).all()
    return incidents

@router.get("/{incident_id}", response_model=IncidentDetailResponse)
def get_incident_detail(incident_id: str, db: Session = Depends(get_db)):
    """Retrieves full incident details, updates timeline, conflicts, and linked source reports."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    
    updates = db.query(IncidentUpdate).filter(IncidentUpdate.incident_id == incident_id).order_by(IncidentUpdate.timestamp.asc()).all()
    conflicts = db.query(IncidentConflict).filter(IncidentConflict.incident_id == incident_id).order_by(IncidentConflict.created_at.desc()).all()
    reports = db.query(RawReport).filter(RawReport.matched_incident_id == incident_id).order_by(RawReport.timestamp.asc()).all()

    reports_data = []
    for r in reports:
        reports_data.append({
            "id": r.id,
            "source": r.source,
            "timestamp": r.timestamp.isoformat(),
            "raw_text": r.raw_text,
            "processing_status": r.processing_status,
            "emergency_type": r.emergency_type,
            "urgency": r.urgency,
            "verification": r.verification,
            "people_affected": r.people_affected,
            "vulnerable_people": r.vulnerable_people,
            "confidence": r.confidence
        })

    return {
        "id": inc.id,
        "title": inc.title,
        "emergency_type": inc.emergency_type,
        "severity": inc.severity,
        "status": inc.status,
        "verification": inc.verification,
        "primary_resource": inc.primary_resource,
        "people_affected": inc.people_affected,
        "vulnerable_people": inc.vulnerable_people,
        "location_name": inc.location_name,
        "interpreted_location": inc.interpreted_location,
        "landmark": inc.landmark,
        "best_known_location": inc.best_known_location,
        "location_confidence": inc.location_confidence,
        "latitude": inc.latitude,
        "longitude": inc.longitude,
        "uncertainty_radius_m": inc.uncertainty_radius_m,
        "summary": inc.summary,
        "confidence": inc.confidence,
        "report_count": inc.report_count,
        "last_escalation_reason": inc.last_escalation_reason,
        "created_at": inc.created_at,
        "updated_at": inc.updated_at,
        "updates": updates,
        "conflicts": conflicts,
        "source_reports": reports_data
    }

@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(incident_id: str, payload: IncidentManualUpdate, db: Session = Depends(get_db)):
    """Allows human responder to override, edit, or adjust incident state with audit logging."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    prev_state = {
        "title": inc.title,
        "severity": inc.severity,
        "status": inc.status,
        "verification": inc.verification,
        "people_affected": inc.people_affected,
        "vulnerable_people": inc.vulnerable_people,
        "primary_resource": inc.primary_resource
    }

    if payload.title is not None:
        inc.title = payload.title
    if payload.emergency_type is not None:
        inc.emergency_type = payload.emergency_type
    if payload.severity is not None:
        inc.severity = payload.severity
    if payload.status is not None:
        inc.status = payload.status
    if payload.verification is not None:
        inc.verification = payload.verification
    if payload.primary_resource is not None:
        inc.primary_resource = payload.primary_resource
    if payload.people_affected is not None:
        inc.people_affected = payload.people_affected
    if payload.vulnerable_people is not None:
        inc.vulnerable_people = payload.vulnerable_people
    if payload.best_known_location is not None:
        inc.best_known_location = payload.best_known_location
    if payload.summary is not None:
        inc.summary = payload.summary

    inc.updated_at = datetime.datetime.utcnow()

    upd = IncidentUpdate(
        incident_id=inc.id,
        update_type="HUMAN_OVERRIDE",
        description=f"Human responder modified incident details: {payload.notes or 'Manual operator update'}.",
        actor="RESPONDER",
        evidence=payload.notes,
        previous_state=prev_state,
        new_state={
            "severity": inc.severity,
            "status": inc.status,
            "people_affected": inc.people_affected,
            "vulnerable_people": inc.vulnerable_people
        }
    )
    db.add(upd)

    audit = AuditLog(
        action=f"RESPONDER_UPDATE_{inc.id}",
        actor="RESPONDER",
        incident_id=inc.id,
        previous_state=str(prev_state),
        new_state=str({"status": inc.status, "severity": inc.severity, "people": inc.people_affected}),
        notes=payload.notes or "Operator manual update"
    )
    db.add(audit)

    db.commit()
    db.refresh(inc)
    return inc

@router.post("/{incident_id}/verify", response_model=IncidentResponse)
def verify_incident(incident_id: str, db: Session = Depends(get_db)):
    """Human responder confirms verification of an unverified incident."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found.")

    old_v = inc.verification
    inc.verification = "Verified"
    inc.confidence = min(0.99, inc.confidence + 0.15)
    inc.updated_at = datetime.datetime.utcnow()

    upd = IncidentUpdate(
        incident_id=inc.id,
        update_type="HUMAN_VERIFIED",
        description="Human responder verified the authenticity of this incident.",
        actor="RESPONDER",
        previous_state={"verification": old_v},
        new_state={"verification": "Verified"}
    )
    db.add(upd)

    audit = AuditLog(
        action="INCIDENT_VERIFIED",
        actor="RESPONDER",
        incident_id=inc.id,
        previous_state=old_v,
        new_state="Verified",
        notes="Human responder confirmed field ground truth."
    )
    db.add(audit)

    db.commit()
    db.refresh(inc)
    return inc

@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(incident_id: str, notes: Optional[str] = "Incident marked resolved by responder", db: Session = Depends(get_db)):
    """Human responder marks incident as RESOLVED."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found.")

    old_status = inc.status
    inc.status = "RESOLVED"
    inc.severity = "Low"
    inc.updated_at = datetime.datetime.utcnow()

    upd = IncidentUpdate(
        incident_id=inc.id,
        update_type="RESOLVED",
        description=f"Responder marked incident as RESOLVED: {notes}.",
        actor="RESPONDER",
        previous_state={"status": old_status},
        new_state={"status": "RESOLVED"}
    )
    db.add(upd)

    audit = AuditLog(
        action="INCIDENT_RESOLVED",
        actor="RESPONDER",
        incident_id=inc.id,
        previous_state=old_status,
        new_state="RESOLVED",
        notes=notes
    )
    db.add(audit)

    db.commit()
    db.refresh(inc)
    return inc

@router.post("/merge", response_model=dict)
def merge_into_incident(payload: IncidentMergeRequest, db: Session = Depends(get_db)):
    """Human responder explicitly merges a flagged report or duplicate incident into a target incident."""
    target = db.query(Incident).filter(Incident.id == payload.target_incident_id).first()
    if not target:
        raise HTTPException(status_code=404, detail=f"Target incident '{payload.target_incident_id}' not found.")

    if payload.report_id:
        rep = db.query(RawReport).filter(RawReport.id == payload.report_id).first()
        if not rep:
            raise HTTPException(status_code=404, detail=f"Report '{payload.report_id}' not found.")
        
        rep.matched_incident_id = target.id
        rep.match_status = "HUMAN_MERGED"
        rep.processing_status = "UPDATED"
        target.report_count += 1
        target.updated_at = datetime.datetime.utcnow()

        upd = IncidentUpdate(
            incident_id=target.id,
            update_type="HUMAN_MERGE",
            description=f"Responder approved merging report {rep.id} into this incident ({payload.reason}).",
            actor="RESPONDER",
            source_report_id=rep.id,
            evidence=rep.raw_text,
            new_state={"report_count": target.report_count}
        )
        db.add(upd)

    db.commit()
    return {"status": "MERGED_SUCCESSFULLY", "target_incident_id": target.id}

@router.post("/{incident_id}/conflicts/{conflict_id}/resolve", response_model=dict)
def resolve_conflict(incident_id: str, conflict_id: int, payload: IncidentResolveConflictRequest, db: Session = Depends(get_db)):
    """Human dispatcher resolves a conflicting information flag (USE_LATEST, KEEP_EXISTING, MANUAL)."""
    conflict = db.query(IncidentConflict).filter(IncidentConflict.id == conflict_id, IncidentConflict.incident_id == incident_id).first()
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict record not found.")

    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found.")

    if payload.action == "USE_LATEST":
        if conflict.field_name == "people_affected":
            inc.people_affected = int(conflict.conflicting_value)
        conflict.status = "RESOLVED_USE_LATEST"
    elif payload.action == "KEEP_EXISTING":
        conflict.status = "RESOLVED_KEEP_EXISTING"
    elif payload.action == "MANUAL" and payload.manual_value:
        if conflict.field_name == "people_affected":
            inc.people_affected = int(payload.manual_value)
        conflict.status = "RESOLVED_MANUAL"

    # If no remaining pending conflicts, restore status from CONFLICTING to ACTIVE
    remaining_conflicts = db.query(IncidentConflict).filter(
        IncidentConflict.incident_id == incident_id,
        IncidentConflict.status == "PENDING_REVIEW",
        IncidentConflict.id != conflict_id
    ).count()

    if remaining_conflicts == 0 and inc.status == "CONFLICTING":
        inc.status = "ACTIVE"

    upd = IncidentUpdate(
        incident_id=inc.id,
        update_type="CONFLICT_RESOLVED",
        description=f"Responder resolved conflicting {conflict.field_name} (Action: {payload.action}).",
        actor="RESPONDER",
        evidence=payload.notes or f"Resolved by dispatcher ({payload.action})",
        new_state={"people_affected": inc.people_affected, "conflict_status": conflict.status}
    )
    db.add(upd)
    db.commit()

    return {"status": "CONFLICT_RESOLVED", "incident_id": incident_id, "action": payload.action}
