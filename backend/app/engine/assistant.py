from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.incident import Incident, IncidentUpdate, IncidentConflict
from app.models.report import RawReport
from app.engine.llm_service import call_gemini_api, call_openai_api

async def answer_responder_query(query: str, db: Session, incident_id: str = None) -> Dict[str, Any]:
    """
    Grounded AI Assistant answering emergency responder queries using live database state.
    """
    q_lower = query.lower()
    
    # Query database for current snapshot
    all_incidents: List[Incident] = db.query(Incident).all()
    recent_updates: List[IncidentUpdate] = db.query(IncidentUpdate).order_by(IncidentUpdate.timestamp.desc()).limit(10).all()
    unverified_reports: List[RawReport] = db.query(RawReport).filter(RawReport.verification == "Unverified", RawReport.is_emergency == True).all()
    conflicts: List[IncidentConflict] = db.query(IncidentConflict).filter(IncidentConflict.status == "PENDING_REVIEW").all()

    # If asking about critical incidents
    if "critical" in q_lower or "highest priority" in q_lower:
        crit_incidents = [inc for inc in all_incidents if inc.severity == "Critical" and inc.status != "RESOLVED"]
        if not crit_incidents:
            return {
                "answer": "There are currently NO active Critical incidents in the queue. All active incidents are at High, Medium, or Low severity.",
                "sources_used": ["Incident DB (Filter: Severity = Critical)"],
                "suggested_actions": ["Review High severity incidents", "Check recent incoming reports"]
            }
        lines = ["**Critical Incidents Requiring Immediate Action:**"]
        for inc in crit_incidents:
            lines.append(f"- **{inc.id}**: {inc.title} ({inc.best_known_location}) — **{inc.people_affected} people affected**. Status: `{inc.status}`. Resource: `{inc.primary_resource}`. {f'Vulnerable: {inc.vulnerable_people}' if inc.vulnerable_people else ''}")
        return {
            "answer": "\n".join(lines),
            "sources_used": [f"Incident {inc.id}" for inc in crit_incidents],
            "suggested_actions": ["Dispatch Rescue / Ambulance", "Monitor Water / Fire levels"]
        }

    # If asking about vulnerable people
    elif "vulnerable" in q_lower or "elderly" in q_lower or "children" in q_lower or "insulin" in q_lower:
        vuln_incidents = [inc for inc in all_incidents if inc.vulnerable_people and inc.status != "RESOLVED"]
        if not vuln_incidents:
            return {
                "answer": "No active incidents currently have vulnerable individuals flagged.",
                "sources_used": ["Incident DB (Filter: vulnerable_people IS NOT NULL)"],
                "suggested_actions": ["Review incoming report feed"]
            }
        lines = ["**Incidents with Identified Vulnerable Persons:**"]
        for inc in vuln_incidents:
            lines.append(f"- **{inc.id}** ({inc.best_known_location}): **{inc.vulnerable_people}**. Resource needed: `{inc.primary_resource}`. Status: `{inc.status}`.")
        return {
            "answer": "\n".join(lines),
            "sources_used": [f"Incident {inc.id}" for inc in vuln_incidents],
            "suggested_actions": ["Prioritize Medical Ambulance", "Notify Field Rescue Team"]
        }

    # If asking about medical emergencies
    elif "medical" in q_lower or "ambulance" in q_lower:
        med_incidents = [inc for inc in all_incidents if (inc.emergency_type == "Medical" or "Medical" in inc.primary_resource) and inc.status != "RESOLVED"]
        if not med_incidents:
            return {
                "answer": "No unresolved medical-specific emergencies currently recorded in the active queue.",
                "sources_used": ["Incident DB"],
                "suggested_actions": ["Check general rescue calls"]
            }
        lines = ["**Active Medical Emergencies & High Medical Need:**"]
        for inc in med_incidents:
            lines.append(f"- **{inc.id}**: {inc.title} ({inc.best_known_location}) — Severity: `{inc.severity}`. People: `{inc.people_affected}`. Resource: `{inc.primary_resource}`.")
        return {
            "answer": "\n".join(lines),
            "sources_used": [f"Incident {inc.id}" for inc in med_incidents],
            "suggested_actions": ["Coordinate with 108 Ambulance Dispatch"]
        }

    # If asking about recent changes
    elif "changed" in q_lower or "recent" in q_lower or "latest" in q_lower:
        if not recent_updates:
            return {
                "answer": "No recent updates logged in the timeline yet.",
                "sources_used": ["Incident Timeline"],
                "suggested_actions": []
            }
        lines = ["**Recent Operational State Changes:**"]
        for upd in recent_updates[:6]:
            t_str = upd.timestamp.strftime("%H:%M:%S")
            lines.append(f"- `[{t_str}]` **{upd.incident_id}** — *{upd.update_type}*: {upd.description}")
        return {
            "answer": "\n".join(lines),
            "sources_used": ["Incident Updates DB"],
            "suggested_actions": ["View Incident Timeline", "Refresh Live Dashboard"]
        }

    # If asking about unverified or rumors
    elif "unverified" in q_lower or "rumor" in q_lower or "pending" in q_lower or "verification" in q_lower:
        unverified_incidents = [inc for inc in all_incidents if inc.verification in ["Unverified", "Partially Verified"] and inc.status != "RESOLVED"]
        lines = [f"**Verification Status Report:** ({len(unverified_incidents)} incidents pending full verification, {len(unverified_reports)} raw unverified reports)"]
        for inc in unverified_incidents[:5]:
            lines.append(f"- **{inc.id}**: {inc.title} — Current Verification: `{inc.verification}` (Confidence: {int(inc.confidence*100)}%, {inc.report_count} reports).")
        lines.append("\n*Reminder: AI recommendations require human dispatcher verification before field deployment.*")
        return {
            "answer": "\n".join(lines),
            "sources_used": ["Reports & Incidents DB"],
            "suggested_actions": ["Open Verification Queue", "Contact Field Observer"]
        }

    # If asking about conflicts
    elif "conflict" in q_lower:
        if not conflicts:
            return {
                "answer": "There are currently NO unresolved conflicting reports in the queue. All incident states are synchronized.",
                "sources_used": ["Incident Conflicts DB"],
                "suggested_actions": []
            }
        lines = ["**Active Conflicting Information Requiring Dispatcher Resolution:**"]
        for c in conflicts:
            lines.append(f"- **Incident {c.incident_id}**: Conflicting field `{c.field_name}` (Existing: `{c.existing_value}` vs Reported: `{c.conflicting_value}`). Confidence: {int(c.confidence*100)}%.")
        return {
            "answer": "\n".join(lines),
            "sources_used": [f"Conflict ID {c.id}" for c in conflicts],
            "suggested_actions": ["Review Conflicting Reports", "Select 'Use Latest' or 'Manual Override'"]
        }

    # Specific Incident Summary (e.g. Velachery)
    elif "velachery" in q_lower or (incident_id and incident_id in q_lower):
        vel_inc = next((inc for inc in all_incidents if "velachery" in inc.title.lower() or "velachery" in inc.best_known_location.lower() or inc.id == incident_id), None)
        if vel_inc:
            lines = [
                f"**Summary of Incident {vel_inc.id} ({vel_inc.title}):**",
                f"- **Type**: {vel_inc.emergency_type} | **Severity**: {vel_inc.severity} | **Status**: `{vel_inc.status}`",
                f"- **Location**: {vel_inc.best_known_location} (Confidence: {int(vel_inc.location_confidence*100)}%)",
                f"- **People Affected**: {vel_inc.people_affected}",
                f"- **Vulnerable Individuals**: {vel_inc.vulnerable_people or 'None reported'}",
                f"- **Primary Resource**: {vel_inc.primary_resource}",
                f"- **Total Corroborating Reports Merged**: {vel_inc.report_count}",
                f"- **Summary**: {vel_inc.summary}"
            ]
            if vel_inc.last_escalation_reason:
                lines.append(f"- **Last Escalation Note**: *{vel_inc.last_escalation_reason}*")
            return {
                "answer": "\n".join(lines),
                "sources_used": [f"Incident {vel_inc.id}", f"{vel_inc.report_count} linked reports"],
                "suggested_actions": ["View Timeline", "Export SitRep"]
            }

    # General / Fallback with LLM attempt if configured
    context_str = f"Current active incidents: {len([i for i in all_incidents if i.status != 'RESOLVED'])}, Critical: {len([i for i in all_incidents if i.severity == 'Critical'])}, People affected: {sum(i.people_affected for i in all_incidents)}."
    
    llm_resp = await call_gemini_api(
        prompt=f"User asked: '{query}'.\nContext: {context_str}\nAnswer concisely as an emergency response assistant based only on provided facts.",
        system_instruction="You are the AI Assistant for Emergency Control Room responders. Be direct, factual, calm, and concise. Never invent false details."
    )
    if llm_resp:
        return {
            "answer": llm_resp,
            "sources_used": ["AI Intelligence Model + Incident DB"],
            "suggested_actions": ["Check Incident Dashboard"]
        }

    return {
        "answer": f"Currently monitoring **{len(all_incidents)} total incidents** ({len([i for i in all_incidents if i.status != 'RESOLVED'])} active). Total people affected across all sectors: **{sum(i.people_affected for i in all_incidents)}**. {len([i for i in all_incidents if i.severity == 'Critical'])} critical incidents in progress.",
        "sources_used": ["Emergency Operations Database"],
        "suggested_actions": ["Filter by Critical", "View Map Overview", "Review Live Reports Feed"]
    }
