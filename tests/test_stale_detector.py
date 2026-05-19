from chrona.intelligence.confidence_scorer import ConfidenceScorer
from chrona.schemas.memory import Memory
from datetime import datetime

def test_stale_detection_via_scorer():
    memory = Memory(
        id="mem-1", incident_id="inc-1", content="Test", summary="Test",
        fix="Test", service="svc", domain="dom", source="src",
        success=True, risk_level="low", timestamp=datetime.now()
    )
    
    score = ConfidenceScorer.score_memory(
        memory=memory,
        semantic_similarity=0.9,
        dependency_overlap=0.1,
        symptom_match=0.1,
        infra_compatibility=0.2, # Low compatibility should trigger stale
        freshness_score=0.9
    )
    
    assert score.status == "stale"
    assert score.staleness_penalty > 0
