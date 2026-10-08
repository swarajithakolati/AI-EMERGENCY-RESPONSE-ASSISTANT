import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Float, Text, JSON, ForeignKey
from app.database import Base

class RawReport(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, index=True) # e.g. REP-1001
    source = Column(String, nullable=False, default="TEXT") # AUDIO, WHATSAPP, SMS, SOCIAL_MEDIA, MANUAL, FILE
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    raw_text = Column(Text, nullable=False)
    processing_status = Column(String, default="RECEIVED") # RECEIVED, ANALYZING, UNDERSTOOD, EXTRACTED, MATCHED, UPDATED, FLAGGED, NOISE
    
    # Classification
    is_emergency = Column(Boolean, default=True)
    is_relevant = Column(Boolean, default=True)
    is_noise = Column(Boolean, default=False)
    is_rumor = Column(Boolean, default=False)
    emergency_type = Column(String, default="Other") # Flood, Fire, Medical, Rescue, Accident, Building collapse, Missing person, Road blockage, Power emergency, Other, None
    urgency = Column(String, default="Medium") # Critical, High, Medium, Low
    verification = Column(String, default="Unverified") # Verified, Partially Verified, Unverified, Conflicting, Unknown
    
    # Extracted data (stored as JSON and top-level fields for fast querying)
    location_raw = Column(String, nullable=True)
    location_interpreted = Column(String, nullable=True)
    landmark = Column(String, nullable=True)
    people_affected = Column(String, nullable=True) # "6", "10", "Unknown"
    vulnerable_people = Column(String, nullable=True)
    resource_needed = Column(String, nullable=True)
    status_signal = Column(String, nullable=True) # "water rising", "trapped", "team reached", "rescued"
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, default=0.5) # 0.0 to 1.0
    
    # Matching / Tracking Link
    matched_incident_id = Column(String, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    match_confidence = Column(Float, default=0.0)
    match_reason = Column(Text, nullable=True)
    match_status = Column(String, default="NONE") # AUTO_MERGED, PENDING_REVIEW, KEPT_SEPARATE, NEW_INCIDENT
    
    # Raw Metadata
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
