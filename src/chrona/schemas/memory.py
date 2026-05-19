from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Memory(BaseModel):
    id: str
    incident_id: str
    content: str
    summary: str
    fix: str
    service: str
    domain: str
    infra_version: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    success: bool
    tags: List[str] = Field(default_factory=list)
    risk_level: str
