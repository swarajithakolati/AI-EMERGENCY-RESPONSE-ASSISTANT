from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.incident import Incident, IncidentUpdate, IncidentConflict
from app.models.report import RawReport
from app.schemas.analytics import AnalyticsSummary

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    """Computes comprehensive live operational and compression analytics."""
    all_reports = db.query(RawReport).all()
    all_incidents = db.query(Incident).all()
    all_updates = db.query(IncidentUpdate).order_by(IncidentUpdate.timestamp.desc()).limit(10).all()
    conflicts_count = db.query(IncidentConflict).filter(IncidentConflict.status == "PENDING_REVIEW").count()

    total_reports = len(all_reports)
    noise_count = sum(1 for r in all_reports if r.is_noise)
    emergency_count = sum(1 for r in all_reports if r.is_emergency and not r.is_noise)
    underlying_count = len(all_incidents)
    
    merged_count = sum(1 for r in all_reports if r.matched_incident_id and r.match_status in ["AUTO_MERGED", "HUMAN_MERGED"])
    
    active_incidents = sum(1 for i in all_incidents if i.status in ["ACTIVE", "ESCALATED", "CONFLICTING"])
    critical_incidents = sum(1 for i in all_incidents if i.severity == "Critical" and i.status != "RESOLVED")
    rescue_in_progress = sum(1 for i in all_incidents if i.status == "RESCUE IN PROGRESS")
    resolved_incidents = sum(1 for i in all_incidents if i.status == "RESOLVED")
    unverified_count = sum(1 for r in all_reports if r.verification in ["Unverified", "Partially Verified"] and r.is_emergency)
    total_people = sum(i.people_affected for i in all_incidents)

    # Calculate compression ratio
    compression_ratio = round((total_reports / underlying_count), 2) if underlying_count > 0 else 1.0

    # Source breakdown
    source_counts = Counter(r.source for r in all_reports)
    
    # Incident breakdown
    type_counts = Counter(i.emergency_type for i in all_incidents)
    severity_counts = Counter(i.severity for i in all_incidents)
    status_counts = Counter(i.status for i in all_incidents)

    recent_timeline = []
    for upd in all_updates:
        recent_timeline.append({
            "id": upd.id,
            "incident_id": upd.incident_id,
            "timestamp": upd.timestamp.isoformat(),
            "update_type": upd.update_type,
            "description": upd.description,
            "actor": upd.actor
        })

    return AnalyticsSummary(
        total_reports=total_reports,
        emergency_reports=emergency_count,
        noise_filtered=noise_count,
        duplicate_reports_merged=merged_count,
        underlying_incidents=underlying_count,
        active_incidents=active_incidents,
        critical_incidents=critical_incidents,
        rescue_in_progress=rescue_in_progress,
        resolved_incidents=resolved_incidents,
        unverified_reports=unverified_count,
        conflicting_reports=conflicts_count,
        total_people_affected=total_people,
        compression_ratio=compression_ratio,
        reports_by_source=dict(source_counts),
        incidents_by_type=dict(type_counts),
        incidents_by_severity=dict(severity_counts),
        incidents_by_status=dict(status_counts),
        recent_activity_timeline=recent_timeline
    )
