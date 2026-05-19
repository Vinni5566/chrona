import logging
from typing import List, Dict, Any

class HindsightClient:
    def __init__(self, api_key: str, project_id: str):
        self.api_key = api_key
        self.project_id = project_id
        
    def store(self, data: Dict[str, Any]) -> bool:
        logging.info(f"Mock Hindsight API: storing memory in project {self.project_id}")
        return True
        
    def search(self, query: str) -> List[Dict[str, Any]]:
        logging.info(f"Mock Hindsight API: searching memory in project {self.project_id}")
        return []
