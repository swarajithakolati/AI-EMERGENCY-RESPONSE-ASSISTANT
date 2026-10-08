from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AIAssistantQuery(BaseModel):
    query: str = Field(..., description="User question to the AI Responder Assistant")
    incident_id: Optional[str] = None
    context_limit: int = 15

class AIAssistantResponse(BaseModel):
    answer: str
    sources_used: List[str] = []
    suggested_actions: List[str] = []
    confidence: float = 0.9

class AIMatchCheckRequest(BaseModel):
    raw_text: str
    incident_id: Optional[str] = None

class AIMatchCheckResponse(BaseModel):
    matched_incident_id: Optional[str] = None
    similarity_score: float
    location_match: str
    type_match: str
    semantic_match: str
    time_proximity: str
    decision: str # AUTO_MERGE, REVIEW_NEEDED, SEPARATE
    reason: str
