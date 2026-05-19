from typing import Dict, Any
from chrona.memory.memory_service import MemoryService
from chrona.intelligence.temporal_decay import TemporalDecayEngine
from chrona.routing.audit_logger import AuditLogger

class ReportService:
    def __init__(self):
        self.memory_service = MemoryService("data/memories")
        self.decay = TemporalDecayEngine()
        self.audit = AuditLogger()
        
    def generate_stale_report(self) -> list:
        memories = self.memory_service.list_memories()
        report = []
        for mem in memories:
            freshness = self.decay.calculate_freshness(mem)
            status = "stale" if freshness < 0.3 else "fresh"
            report.append({
                "id": mem.id,
                "service": mem.service,
                "status": status,
                "freshness": freshness,
                "reason": "Low freshness score" if status == "stale" else "High freshness score"
            })
        return report

    def get_route_stats(self) -> dict:
        return self.audit.get_stats()
