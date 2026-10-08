import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    action = Column(String, nullable=False) # e.g. "REPORT_CLASSIFIED", "INCIDENT_CREATED", "INCIDENT_MERGED", "URGENCY_ESCALATED", "STATUS_UPDATED", "HUMAN_VERIFIED"
    actor = Column(String, default="AI") # AI or RESPONDER
    source = Column(String, nullable=True) # AUDIO, WHATSAPP, CONTROL_ROOM, etc.
    incident_id = Column(String, nullable=True, index=True)
    report_id = Column(String, nullable=True, index=True)
    previous_state = Column(Text, nullable=True)
    new_state = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict)
