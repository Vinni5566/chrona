from datetime import datetime, timezone, timedelta
from chrona.intelligence.temporal_decay import TemporalDecayEngine
from chrona.schemas.memory import Memory

def test_freshness_decay():
    engine = TemporalDecayEngine(decay_lambda=0.01)
    
    now = datetime.now(timezone.utc)
    old_time = now - timedelta(days=100)
    
    memory = Memory(
        id="mem-1",
        incident_id="inc-1",
        content="Test",
        summary="Test",
        fix="Test",
        service="svc",
        domain="dom",
        source="src",
        success=True,
        risk_level="low",
        timestamp=old_time
    )
    
    score = engine.calculate_freshness(memory)
    assert 0.0 < score < 0.4  # exp(-1) is ~0.36
