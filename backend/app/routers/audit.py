from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit import AuditLog

router = APIRouter(prefix="/api/audit", tags=["Audit Log"])

@router.get("", response_model=List[dict])
def list_audit_logs(
    actor: Optional[str] = None,
    incident_id: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db)
):
    """Returns chronological audit logs tracking all AI and Human actions."""
    query = db.query(AuditLog)
    if actor:
        query = query.filter(AuditLog.actor == actor.upper())
    if incident_id:
        query = query.filter(AuditLog.incident_id == incident_id)

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    return [{
        "id": log.id,
        "timestamp": log.timestamp.isoformat(),
        "action": log.action,
        "actor": log.actor,
        "source": log.source,
        "incident_id": log.incident_id,
        "report_id": log.report_id,
        "previous_state": log.previous_state,
        "new_state": log.new_state,
        "notes": log.notes
    } for log in logs]
