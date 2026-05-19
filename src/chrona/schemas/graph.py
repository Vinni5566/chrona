from pydantic import BaseModel, Field
from typing import Dict, Any

class GraphNode(BaseModel):
    id: str
    type: str  # repo/domain/service/api/database/queue/config/incident
    name: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
