from chrona.config.settings import settings
from chrona.schemas.routing import RoutingDecision
from chrona.routing.audit_logger import AuditLogger

class CascadeflowRouter:
    def __init__(self):
        self.audit_logger = AuditLogger()
        self.cheap_models = ["llama3-8b", "qwen/qwen-1.5-7b"]
        self.mid_models = ["llama-3.3-70b-versatile", "qwen/qwen3-32b"]
        self.strong_models = [settings.CASCADEFLOW_DEFAULT_MODEL, "gpt-4", "gpt-4o"]

    def route_task(self, task_type: str, severity: str, confidence_score: float, context_size: int) -> RoutingDecision:
        # Determine weights
        severity_weights = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}
        sev_weight = severity_weights.get(severity.lower(), 0.5)

        task_weights = {
            "generate_rca": 0.9,
            "suggest_remediation": 0.85,
            "draft_postmortem": 0.8,
            "summarize_logs": 0.4,
            "classify_incident": 0.3
        }
        task_weight = task_weights.get(task_type.lower(), 0.5)

        # Estimate context token volume (approx 1.3 tokens per word/character block)
        estimated_tokens = int(context_size * 1.3)
        
        # Heuristic scoring system
        # routing_score = 40% severity + 40% task complexity + 20% uncertainty (1 - confidence)
        uncertainty = 1.0 - max(0.0, min(1.0, confidence_score))
        routing_score = (sev_weight * 0.4) + (task_weight * 0.4) + (uncertainty * 0.2)

        # Check for context limits or extreme urgency
        force_strong = (severity.lower() == "critical") or (estimated_tokens > 8000)

        # Model selection logic
        if force_strong or routing_score >= 0.75:
            selected_model = self.strong_models[0]
            tier = "strong (High-Intelligence Reasoning)"
            fallback_model = self.mid_models[0]
            # Pricing for strong models (approx $2.50 per M input, $10.00 per M output)
            estimated_cost = ((estimated_tokens / 1_000_000) * 2.50) + ((500 / 1_000_000) * 10.00)
        elif routing_score >= 0.45:
            selected_model = self.mid_models[0]
            tier = "mid-tier (Balanced Cost-to-Performance)"
            fallback_model = self.cheap_models[0]
            # Pricing for mid models (approx $0.59 per M input, $0.79 per M output)
            estimated_cost = ((estimated_tokens / 1_000_000) * 0.59) + ((400 / 1_000_000) * 0.79)
        else:
            selected_model = self.cheap_models[0]
            tier = "cheap (Sub-millisecond Latency)"
            fallback_model = self.mid_models[0]
            # Pricing for cheap models (approx $0.05 per M input, $0.08 per M output)
            estimated_cost = ((estimated_tokens / 1_000_000) * 0.05) + ((250 / 1_000_000) * 0.08)

        # Build comprehensive routing explanation
        reason = (
            f"Routed to {tier} model '{selected_model}' based on: "
            f"Routing score of {routing_score:.2f} (Severity Weight: {sev_weight:.2f}, "
            f"Task Complexity: {task_weight:.2f}, Context: {estimated_tokens} tokens)."
        )
        if force_strong:
            reason += " [FORCED STRONG due to critical severity or large context]"

        decision = RoutingDecision(
            task_type=task_type,
            selected_model=selected_model,
            reason=reason,
            estimated_cost=max(0.0001, round(estimated_cost, 6)),
            latency_priority="high" if severity.lower() in ["critical", "high"] else "normal",
            fallback_model=fallback_model
        )

        self.audit_logger.log_decision(decision)
        return decision
