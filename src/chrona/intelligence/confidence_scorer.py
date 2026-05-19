from chrona.schemas.scoring import MemoryScore
from chrona.schemas.memory import Memory

class ConfidenceScorer:
    @staticmethod
    def score_memory(
        memory: Memory, 
        semantic_similarity: float,
        dependency_overlap: float,
        symptom_match: float,
        infra_compatibility: float,
        freshness_score: float
    ) -> MemoryScore:
        
        staleness_penalty = 0.0
        
        if infra_compatibility < 0.3:
            status = "stale"
            staleness_penalty = 0.4
            explanation = f"Memory marked stale because infra compatibility is low ({infra_compatibility:.2f})."
        elif infra_compatibility < 0.5 and freshness_score < 0.5:
            status = "dangerous"
            staleness_penalty = 0.6
            explanation = "Dangerous memory: old and incompatible with current infra."
        elif freshness_score > 0.8:
            status = "fresh"
            explanation = "Memory is fresh and applicable."
        elif dependency_overlap > 0.7 or symptom_match > 0.7:
            status = "historical_useful"
            explanation = "Memory is old but highly relevant due to shared dependencies or symptoms."
        else:
            status = "unknown"
            explanation = "Memory relevance is uncertain."

        final_score = (
            0.30 * semantic_similarity +
            0.25 * dependency_overlap +
            0.20 * symptom_match +
            0.15 * infra_compatibility +
            0.10 * freshness_score -
            staleness_penalty
        )
        
        final_score = max(0.0, min(1.0, final_score))
        
        return MemoryScore(
            semantic_similarity=semantic_similarity,
            freshness_score=freshness_score,
            dependency_overlap=dependency_overlap,
            symptom_match=symptom_match,
            infra_compatibility=infra_compatibility,
            staleness_penalty=staleness_penalty,
            final_score=final_score,
            status=status,
            explanation=explanation
        )
