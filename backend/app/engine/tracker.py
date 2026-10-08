import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.incident import Incident, IncidentUpdate, IncidentConflict
from app.models.report import RawReport
from app.models.audit import AuditLog

def apply_report_to_incident(
    db: Session,
    incident: Incident,
    report: RawReport,
    extracted: Dict[str, Any],
    actor: str = "AI"
) -> List[IncidentUpdate]:
    """
    Applies an incoming report to an existing incident record, updating state,
    detecting escalations, conflicts, vulnerabilities, and writing audit + timeline entries.
    """
    created_updates = []
    prev_state = {
        "severity": incident.severity,
        "status": incident.status,
        "people_affected": incident.people_affected,
        "vulnerable_people": incident.vulnerable_people,
        "primary_resource": incident.primary_resource,
        "verification": incident.verification,
        "report_count": incident.report_count
    }

    # Increment report count
    incident.report_count += 1
    incident.updated_at = datetime.datetime.utcnow()

    # Link report
    report.matched_incident_id = incident.id
    report.match_status = "AUTO_MERGED"

    # Multi-source confirmation boosting
    if incident.report_count >= 2 and incident.verification == "Unverified":
        incident.verification = "Partially Verified"
        incident.confidence = min(0.95, incident.confidence + 0.12)
    elif incident.report_count >= 3:
        incident.verification = "Verified"
        incident.confidence = min(0.98, incident.confidence + 0.08)

    # 1. PEOPLE COUNT UPDATE / CONFLICT DETECTION
    new_people = extracted.get("people_affected")
    if new_people is not None:
        if incident.people_affected == 0:
            incident.people_affected = new_people
            upd = IncidentUpdate(
                incident_id=incident.id,
                update_type="PEOPLE_COUNT_UPDATED",
                description=f"People affected identified as {new_people}.",
                actor=actor,
                source_report_id=report.id,
                evidence=report.raw_text,
                previous_state={"people_affected": 0},
                new_state={"people_affected": new_people}
            )
            db.add(upd)
            created_updates.append(upd)
        elif new_people > incident.people_affected:
            old_p = incident.people_affected
            incident.people_affected = new_people
            # Auto escalate severity if count increases significantly
            if new_people >= 10 and incident.severity != "Critical":
                incident.severity = "Critical"
                incident.last_escalation_reason = f"People affected increased from {old_p} to {new_people}."

            upd = IncidentUpdate(
                incident_id=incident.id,
                update_type="PEOPLE_COUNT_UPDATED",
                description=f"People affected count increased: {old_p} → {new_people}.",
                actor=actor,
                source_report_id=report.id,
                evidence=f"Report indicates {new_people} people now affected.",
                previous_state={"people_affected": old_p},
                new_state={"people_affected": new_people}
            )
            db.add(upd)
            created_updates.append(upd)
        elif new_people < incident.people_affected and (incident.people_affected - new_people) >= 3:
            # Conflicting lower count reported without resolution signal -> flag conflict
            status_sig = extracted.get("status_signal")
            if status_sig not in ["RESOLVED", "RESCUE_IN_PROGRESS"]:
                conflict = IncidentConflict(
                    incident_id=incident.id,
                    report_id=report.id,
                    field_name="people_affected",
                    existing_value=str(incident.people_affected),
                    conflicting_value=str(new_people),
                    confidence=0.67,
                    status="PENDING_REVIEW"
                )
                db.add(conflict)
                incident.status = "CONFLICTING"
                upd = IncidentUpdate(
                    incident_id=incident.id,
                    update_type="CONFLICT_FLAGGED",
                    description=f"Conflicting people count reported: {new_people} vs current {incident.people_affected}.",
                    actor="AI",
                    source_report_id=report.id,
                    evidence="Conflicting headcounts received from multiple reports.",
                    previous_state={"people_affected": incident.people_affected},
                    new_state={"conflicting_report_value": new_people}
                )
                db.add(upd)
                created_updates.append(upd)

    # 2. VULNERABLE PERSON DETECTION
    new_vuln = extracted.get("vulnerable_people")
    if new_vuln:
        if not incident.vulnerable_people or new_vuln not in incident.vulnerable_people:
            old_v = incident.vulnerable_people
            if incident.vulnerable_people:
                incident.vulnerable_people = f"{incident.vulnerable_people}, {new_vuln}"
            else:
                incident.vulnerable_people = new_vuln

            # Escalate urgency & resource
            if "Insulin" in new_vuln or "Medical" in new_vuln or "Elderly" in new_vuln:
                incident.severity = "Critical"
                incident.primary_resource = "Rescue Team + Medical Ambulance (Insulin/Emergency Support)"
                incident.last_escalation_reason = f"Identified vulnerable person ({new_vuln}) requiring urgent medical/rescue intervention."

            upd = IncidentUpdate(
                incident_id=incident.id,
                update_type="VULNERABILITY_DETECTED",
                description=f"Vulnerable person detected: {new_vuln}.",
                actor=actor,
                source_report_id=report.id,
                evidence=f"Report mentions: {new_vuln}",
                previous_state={"vulnerable_people": old_v},
                new_state={"vulnerable_people": incident.vulnerable_people}
            )
            db.add(upd)
            created_updates.append(upd)

    # 3. STATUS SIGNAL / PROGRESSION DETECTION
    sig = extracted.get("status_signal")
    if sig == "RESOLVED":
        old_status = incident.status
        incident.status = "RESOLVED"
        incident.severity = "Low"
        upd = IncidentUpdate(
            incident_id=incident.id,
            update_type="RESOLVED",
            description="Incident successfully resolved: all affected persons safely rescued.",
            actor=actor,
            source_report_id=report.id,
            evidence="Field report confirms rescue operation completed.",
            previous_state={"status": old_status},
            new_state={"status": "RESOLVED"}
        )
        db.add(upd)
        created_updates.append(upd)
    elif sig == "RESCUE_IN_PROGRESS" and incident.status != "RESOLVED":
        old_status = incident.status
        incident.status = "RESCUE IN PROGRESS"
        upd = IncidentUpdate(
            incident_id=incident.id,
            update_type="STATUS_CHANGED",
            description="Rescue operation commenced on site: emergency teams deployed.",
            actor=actor,
            source_report_id=report.id,
            evidence="Confirmation that rescue teams/boats have reached the location.",
            previous_state={"status": old_status},
            new_state={"status": "RESCUE IN PROGRESS"}
        )
        db.add(upd)
        created_updates.append(upd)
    elif sig == "ESCALATED" and incident.status not in ["RESOLVED", "RESCUE IN PROGRESS"]:
        old_status = incident.status
        incident.status = "ESCALATED"
        incident.severity = "Critical"
        incident.last_escalation_reason = "Environmental escalation reported: water rising / conditions deteriorating rapidly."
        upd = IncidentUpdate(
            incident_id=incident.id,
            update_type="ESCALATED",
            description="Incident escalated: environmental hazards worsening (water rising).",
            actor=actor,
            source_report_id=report.id,
            evidence="Multiple reports indicate rising water levels.",
            previous_state={"status": old_status, "severity": prev_state["severity"]},
            new_state={"status": "ESCALATED", "severity": "Critical"}
        )
        db.add(upd)
        created_updates.append(upd)
    else:
        # Standard report attachment timeline update if no specific trigger fired
        if not created_updates:
            upd = IncidentUpdate(
                incident_id=incident.id,
                update_type="REPORT_ATTACHED",
                description=f"Corroborating report received from {report.source}.",
                actor=actor,
                source_report_id=report.id,
                evidence=report.raw_text[:120],
                previous_state=prev_state,
                new_state={"report_count": incident.report_count}
            )
            db.add(upd)
            created_updates.append(upd)

    # 4. Location refinement if newer report has richer landmark
    new_lm = extracted.get("landmark")
    if new_lm and (not incident.landmark or len(new_lm) > len(incident.landmark or "")):
        incident.landmark = new_lm
        incident.best_known_location = f"{incident.interpreted_location or incident.location_name} — {new_lm}"
        incident.location_confidence = min(0.92, incident.location_confidence + 0.05)

    # 5. Create Audit Log Entry
    audit = AuditLog(
        action=f"INCIDENT_UPDATED_{incident.id}",
        actor=actor,
        source=report.source,
        incident_id=incident.id,
        report_id=report.id,
        previous_state=str(prev_state),
        new_state=str({
            "severity": incident.severity,
            "status": incident.status,
            "people_affected": incident.people_affected,
            "vulnerable_people": incident.vulnerable_people,
            "report_count": incident.report_count
        }),
        notes=f"Updated incident from report '{report.id}'"
    )
    db.add(audit)

    return created_updates
