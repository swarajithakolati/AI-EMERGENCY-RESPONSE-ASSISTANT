from typing import Dict, List, Any
from pydantic import BaseModel

class AnalyticsSummary(BaseModel):
    total_reports: int
    emergency_reports: int
    noise_filtered: int
    duplicate_reports_merged: int
    underlying_incidents: int
    active_incidents: int
    critical_incidents: int
    rescue_in_progress: int
    resolved_incidents: int
    unverified_reports: int
    conflicting_reports: int
    total_people_affected: int
    compression_ratio: float # e.g. 5.2x
    reports_by_source: Dict[str, int]
    incidents_by_type: Dict[str, int]
    incidents_by_severity: Dict[str, int]
    incidents_by_status: Dict[str, int]
    recent_activity_timeline: List[Dict[str, Any]]
