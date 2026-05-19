from typing import Dict, Any
from chrona.schemas.incident import Incident
from chrona.intelligence.sanitizer import Sanitizer
from chrona.graph.graph_store import GraphStore
from chrona.memory.memory_service import MemoryService
from chrona.memory.vector_store import VectorStore
from chrona.retrieval.hybrid_retriever import HybridRetriever
from chrona.routing.cascadeflow_router import CascadeflowRouter
from chrona.llm.llm_client import LLMClient
from datetime import datetime

class IncidentService:
    def __init__(self):
        self.graph_store = GraphStore("data/graph")
        self.memory_service = MemoryService("data/memories")
        self.vector_store = VectorStore()
        self._init_vector_store()
        
        self.graph = self.graph_store.load()
        self.retriever = HybridRetriever(self.memory_service, self.vector_store, self.graph)
        self.router = CascadeflowRouter()
        self.llm = LLMClient()
        
    def _init_vector_store(self):
        memories = self.memory_service.list_memories()
        for mem in memories:
            self.vector_store.add(mem)

    def analyze_query(self, query: str) -> Dict[str, Any]:
        incident = Incident(
            id=f"inc-{int(datetime.now().timestamp())}",
            title=query[:50],
            description=query,
            severity="high",
            environment="production",
            metadata={"infra_version": "1.0"}
        )
        
        incident = Sanitizer.sanitize_incident(incident)
        incident_context = incident.model_dump()
        retrieved_memories = self.retriever.retrieve(query, incident_context)
        
        decision = self.router.route_task(
            task_type="generate_rca",
            severity=incident.severity,
            confidence_score=0.8,
            context_size=len(retrieved_memories) * 100
        )
        
        safe_context = {
            "incident": incident.model_dump(),
            "retrieved_memories": retrieved_memories
        }
        safe_context = Sanitizer.sanitize_context(safe_context)
        llm_response = self.llm.execute_task(decision.selected_model, decision.task_type, safe_context)
        
        return {
            "incident": incident,
            "memories": retrieved_memories,
            "routing": decision,
            "llm_response": llm_response
        }
