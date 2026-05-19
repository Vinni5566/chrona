from typing import List, Dict, Any
import networkx as nx
from chrona.memory.memory_service import MemoryService
from chrona.memory.vector_store import VectorStore
from chrona.intelligence.temporal_decay import TemporalDecayEngine
from chrona.intelligence.confidence_scorer import ConfidenceScorer
from chrona.retrieval.causal_recall import CausalRecall

class HybridRetriever:
    def __init__(self, memory_service: MemoryService, vector_store: VectorStore, graph: nx.DiGraph):
        self.memory_service = memory_service
        self.vector_store = vector_store
        self.graph = graph
        self.decay_engine = TemporalDecayEngine()
        self.causal_recall = CausalRecall(graph)

    def retrieve(self, query: str, incident_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        affected_services = incident_context.get("affected_services", [])
        if not affected_services:
            for node in self.graph.nodes():
                if node.startswith("service:") and node.replace("service:", "") in query:
                    affected_services.append(node.replace("service:", ""))
                    
        semantic_results = self.vector_store.search(query, top_k=10)
        
        final_results = []
        for mem, semantic_score in semantic_results:
            freshness = self.decay_engine.calculate_freshness(mem)
            symptom_match = 0.8 if any(sym.lower() in query.lower() for sym in mem.tags) else 0.2
            
            current_infra_version = incident_context.get("metadata", {}).get("infra_version", "1.0")
            infra_compat = 1.0 if mem.infra_version == current_infra_version else 0.2
            
            dep_overlap = 0.5
            causal_links = []
            if affected_services and mem.service not in affected_services:
                links = self.causal_recall.find_causal_links(affected_services[0], [mem])
                if links:
                    dep_overlap = links[0][1]
                    causal_links.append(links[0][2])
            elif affected_services and mem.service in affected_services:
                dep_overlap = 1.0

            score_obj = ConfidenceScorer.score_memory(
                memory=mem,
                semantic_similarity=semantic_score,
                dependency_overlap=dep_overlap,
                symptom_match=symptom_match,
                infra_compatibility=infra_compat,
                freshness_score=freshness
            )
            
            final_results.append({
                "memory": mem,
                "score": score_obj,
                "causal_links": causal_links
            })
            
        final_results.sort(key=lambda x: x["score"].final_score, reverse=True)
        return final_results
