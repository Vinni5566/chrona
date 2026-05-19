import json
from pathlib import Path
from typing import List, Dict, Any, Optional

class LocalMemoryStore:
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.memories_file = self.storage_dir / "memories.json"
        
    def _load(self) -> Dict[str, Any]:
        if not self.memories_file.exists():
            return {}
        try:
            with open(self.memories_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _save(self, data: Dict[str, Any]):
        with open(self.memories_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def store(self, memory_id: str, data: Dict[str, Any]):
        memories = self._load()
        memories[memory_id] = data
        self._save(memories)

    def retrieve_all(self) -> List[Dict[str, Any]]:
        return list(self._load().values())

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        return self._load().get(memory_id)
        
    def update(self, memory_id: str, updates: Dict[str, Any]):
        memories = self._load()
        if memory_id in memories:
            memories[memory_id].update(updates)
            self._save(memories)
