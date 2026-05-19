from chrona.services.incident_service import IncidentService

class ReplayService:
    def __init__(self):
        self.incident_service = IncidentService()
        
    def replay(self, incident_id: str) -> dict:
        query = "checkout API latency spiked but Redis looks healthy"
        return self.incident_service.analyze_query(query)
