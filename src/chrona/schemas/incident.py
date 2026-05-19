from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Incident(BaseModel):
    id: str
    title: str
    description: str
    logs: Optional[str] = None
    affected_services: List[str] = Field(default_factory=list)
    symptoms: List[str] = Field(default_factory=list)
    severity: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    environment: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
