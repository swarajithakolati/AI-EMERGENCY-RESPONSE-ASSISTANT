from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class IncidentUpdateResponse(BaseModel):
    id: int
    incident_id: str
    timestamp: datetime
    update_type: str
    description: str
    actor: str
    evidence: Optional[str] = None
    source_report_id: Optional[str] = None
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class IncidentConflictResponse(BaseModel):
    id: int
    incident_id: str
    report_id: str
    field_name: str
    existing_value: str
    conflicting_value: str
    confidence: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class IncidentResponse(BaseModel):
    id: str
    title: str
    emergency_type: str
    severity: str
    status: str
    verification: str
    primary_resource: str
    people_affected: int
    vulnerable_people: Optional[str] = None
    location_name: Optional[str] = None
    interpreted_location: Optional[str] = None
    landmark: Optional[str] = None
    best_known_location: str
    location_confidence: float
    latitude: float
    longitude: float
    uncertainty_radius_m: float
    summary: str
    confidence: float
    report_count: int
    last_escalation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IncidentDetailResponse(IncidentResponse):
    updates: List[IncidentUpdateResponse] = []
    conflicts: List[IncidentConflictResponse] = []
    source_reports: List[Dict[str, Any]] = []

class IncidentManualUpdate(BaseModel):
    title: Optional[str] = None
    emergency_type: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    verification: Optional[str] = None
    primary_resource: Optional[str] = None
    people_affected: Optional[int] = None
    vulnerable_people: Optional[str] = None
    best_known_location: Optional[str] = None
    summary: Optional[str] = None
    notes: Optional[str] = None

class IncidentMergeRequest(BaseModel):
    target_incident_id: str
    report_id: Optional[str] = None
    source_incident_id: Optional[str] = None
    reason: Optional[str] = "Manual operator merge"

class IncidentResolveConflictRequest(BaseModel):
    action: str = Field(..., description="USE_LATEST, KEEP_EXISTING, MANUAL")
    manual_value: Optional[str] = None
    notes: Optional[str] = None
