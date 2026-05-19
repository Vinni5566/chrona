from pydantic import BaseModel
from typing import Literal

class MemoryScore(BaseModel):
    semantic_similarity: float
    freshness_score: float
    dependency_overlap: float
    symptom_match: float
    infra_compatibility: float
    staleness_penalty: float
    final_score: float
    status: Literal["fresh", "historical_useful", "stale", "dangerous", "unknown"]
    explanation: str
