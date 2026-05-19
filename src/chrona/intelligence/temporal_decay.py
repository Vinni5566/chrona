import math
from datetime import datetime, timezone
from chrona.schemas.memory import Memory

class TemporalDecayEngine:
    def __init__(self, decay_lambda: float = 0.01):
        self.decay_lambda = decay_lambda

    def calculate_freshness(self, memory: Memory) -> float:
        now = datetime.now(timezone.utc)
        mem_time = memory.timestamp
        if mem_time.tzinfo is None:
            mem_time = mem_time.replace(tzinfo=timezone.utc)
            
        age_days = (now - mem_time).days
        if age_days < 0:
            age_days = 0
            
        score = math.exp(-self.decay_lambda * age_days)
        return max(0.0, min(1.0, score))
