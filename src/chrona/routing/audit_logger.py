import json
import os
from datetime import datetime, timezone
from pathlib import Path
from chrona.config.settings import settings
from chrona.schemas.routing import RoutingDecision

class AuditLogger:
    def __init__(self):
        self.audit_dir = Path("data/audit")
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.audit_dir / "routing_audit.jsonl"

    def log_decision(self, decision: RoutingDecision):
        if not settings.CHRONA_ENABLE_AUDIT_LOGS:
            return
            
        record = decision.model_dump()
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
            
    def get_stats(self) -> dict:
        if not self.audit_file.exists():
            return {}
            
        stats = {
            "total_calls": 0,
            "models_used": {},
            "total_cost": 0.0,
            "fallbacks": 0
        }
        
        with open(self.audit_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                record = json.loads(line)
                stats["total_calls"] += 1
                model = record.get("selected_model", "unknown")
                stats["models_used"][model] = stats["models_used"].get(model, 0) + 1
                stats["total_cost"] += record.get("estimated_cost", 0.0)
                if record.get("fallback_model"):
                    stats["fallbacks"] += 1
                    
        return stats
