import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True) # e.g. INC-1001
    title = Column(String, nullable=False)
    emergency_type = Column(String, nullable=False) # Flood, Fire, Medical, Rescue, Building collapse, etc.
    severity = Column(String, default="Medium") # Critical, High, Medium, Low
    status = Column(String, default="ACTIVE") # ACTIVE, ESCALATED, RESCUE IN PROGRESS, RESOLVED, UNVERIFIED, CONFLICTING
    verification = Column(String, default="Unverified") # Verified, Partially Verified, Unverified, Conflicting
    primary_resource = Column(String, default="Rescue team")
    
    # Numbers and Vulnerability
    people_affected = Column(Integer, default=0)
    vulnerable_people = Column(String, nullable=True) # e.g. "1 elderly person requiring insulin"
    
    # Location Intelligence
    location_name = Column(String, nullable=True)
    interpreted_location = Column(String, nullable=True)
    landmark = Column(String, nullable=True)
    best_known_location = Column(String, nullable=False)
    location_confidence = Column(Float, default=0.7)
    latitude = Column(Float, default=12.9716) # default Chennai/Metro area
    longitude = Column(Float, default=80.2206)
    uncertainty_radius_m = Column(Float, default=300.0)
    
    # Summary & Intelligence
    summary = Column(Text, nullable=False)
    confidence = Column(Float, default=0.75)
    report_count = Column(Integer, default=1)
    
    # Escalation & History
    last_escalation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    updates = relationship("IncidentUpdate", back_populates="incident", cascade="all, delete-orphan", order_by="IncidentUpdate.timestamp.asc()")
    conflicts = relationship("IncidentConflict", back_populates="incident", cascade="all, delete-orphan")


class IncidentUpdate(Base):
    __tablename__ = "incident_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    update_type = Column(String, nullable=False) # CREATED, REPORT_ATTACHED, PEOPLE_COUNT_UPDATED, VULNERABILITY_DETECTED, ESCALATED, STATUS_CHANGED, RESOLVED, HUMAN_MERGE, HUMAN_OVERRIDE, CONFLICT_FLAGGED
    description = Column(Text, nullable=False)
    actor = Column(String, default="AI") # AI or RESPONDER
    evidence = Column(Text, nullable=True)
    source_report_id = Column(String, nullable=True)
    
    previous_state = Column(JSON, default=dict)
    new_state = Column(JSON, default=dict)

    incident = relationship("Incident", back_populates="updates")


class IncidentConflict(Base):
    __tablename__ = "incident_conflicts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    report_id = Column(String, nullable=False)
    field_name = Column(String, nullable=False) # "people_affected", "urgency", "location"
    existing_value = Column(String, nullable=False)
    conflicting_value = Column(String, nullable=False)
    confidence = Column(Float, default=0.6)
    status = Column(String, default="PENDING_REVIEW") # PENDING_REVIEW, RESOLVED_USE_LATEST, RESOLVED_KEEP_EXISTING, RESOLVED_MANUAL
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    incident = relationship("Incident", back_populates="conflicts")
