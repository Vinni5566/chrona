from pydantic import BaseModel
from typing import Optional

class RoutingDecision(BaseModel):
    task_type: str
    selected_model: str
    reason: str
    estimated_cost: float
    latency_priority: str
    fallback_model: Optional[str] = None
