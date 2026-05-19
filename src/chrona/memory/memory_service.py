import os
from typing import List, Optional, Dict, Any
from chrona.memory.hindsight_client import HindsightClient
from chrona.memory.local_memory_store import LocalMemoryStore
from chrona.schemas.memory import Memory

class MemoryService:
    def __init__(self, data_dir: str = "data/memories"):
        self.storage_mode = os.environ.get("CHRONA_STORAGE_MODE", "local")
        self.local_store = LocalMemoryStore(data_dir)
        
        api_key = os.environ.get("HINDSIGHT_API_KEY")
        project_id = os.environ.get("HINDSIGHT_PROJECT_ID")
        
        if self.storage_mode == "hindsight" and api_key and project_id:
            self.hindsight_client = HindsightClient(api_key, project_id)
        else:
            if self.storage_mode == "hindsight":
                print("Warning: Hindsight credentials missing, falling back to local storage.")
            self.hindsight_client = None

    def store_memory(self, memory: Memory):
        data = memory.model_dump()
        data["timestamp"] = data["timestamp"].isoformat()
        
        self.local_store.store(memory.id, data)
        if self.hindsight_client:
            self.hindsight_client.store(data)

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        data = self.local_store.get(memory_id)
        if data:
            return Memory(**data)
        return None

    def list_memories(self) -> List[Memory]:
        return [Memory(**m) for m in self.local_store.retrieve_all()]

    def update_memory(self, memory_id: str, updates: Dict[str, Any]):
        self.local_store.update(memory_id, updates)
