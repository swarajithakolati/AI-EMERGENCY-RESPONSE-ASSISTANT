from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class ReportCreate(BaseModel):
    source: str = Field(default="TEXT", description="AUDIO, WHATSAPP, SMS, SOCIAL_MEDIA, MANUAL, FILE")
    raw_text: str = Field(..., description="Original raw incoming text")
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class ReportBatchCreate(BaseModel):
    reports: List[ReportCreate]

class ExtractedInfo(BaseModel):
    is_emergency: bool = True
    is_relevant: bool = True
    is_noise: bool = False
    is_rumor: bool = False
    emergency_type: str = "Other"
    urgency: str = "Medium"
    verification: str = "Unverified"
    location_raw: Optional[str] = None
    location_interpreted: Optional[str] = None
    landmark: Optional[str] = None
    best_known_location: Optional[str] = None
    location_confidence: float = 0.5
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    people_affected: Optional[int] = None
    vulnerable_people: Optional[str] = None
    resource_needed: Optional[str] = None
    status_signal: Optional[str] = None
    evidence: Optional[str] = None
    confidence: float = 0.5

class RawReportResponse(BaseModel):
    id: str
    source: str
    timestamp: datetime
    raw_text: str
    processing_status: str
    is_emergency: bool
    is_relevant: bool
    is_noise: bool
    is_rumor: bool
    emergency_type: str
    urgency: str
    verification: str
    location_raw: Optional[str] = None
    location_interpreted: Optional[str] = None
    landmark: Optional[str] = None
    people_affected: Optional[str] = None
    vulnerable_people: Optional[str] = None
    resource_needed: Optional[str] = None
    status_signal: Optional[str] = None
    evidence: Optional[str] = None
    confidence: float
    matched_incident_id: Optional[str] = None
    match_confidence: float = 0.0
    match_reason: Optional[str] = None
    match_status: str = "NONE"
    created_at: datetime

    class Config:
        from_attributes = True
