from chrona.config.settings import settings
from chrona.schemas.routing import RoutingDecision
from chrona.routing.audit_logger import AuditLogger

class CascadeflowRouter:
    def __init__(self):
        self.audit_logger = AuditLogger()
        self.cheap_models = ["llama3-8b", "qwen/qwen-1.5-7b"]
        self.strong_models = [settings.CASCADEFLOW_DEFAULT_MODEL, "gpt-4"]

    def route_task(self, task_type: str, severity: str, confidence_score: float, context_size: int) -> RoutingDecision:
        is_complex = task_type in ["generate_rca", "suggest_remediation", "draft_postmortem"]
        needs_strong = is_complex or severity in ["high", "critical"] or confidence_score < 0.5
        
        selected_model = self.strong_models[0] if needs_strong else self.cheap_models[0]
        fallback_model = settings.CASCADEFLOW_FALLBACK_MODEL
        
        decision = RoutingDecision(
            task_type=task_type,
            selected_model=selected_model,
            reason="High severity or complex task requires strong model." if needs_strong else "Simple task routed to cheap model.",
            estimated_cost=0.05 if needs_strong else 0.001,
            latency_priority="high" if severity == "critical" else "normal",
            fallback_model=fallback_model
        )
        
        self.audit_logger.log_decision(decision)
        return decision
