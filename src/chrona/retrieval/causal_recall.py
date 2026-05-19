from typing import List, Tuple
import networkx as nx
from chrona.graph.graph_query import GraphQuery
from chrona.schemas.memory import Memory

class CausalRecall:
    def __init__(self, graph: nx.DiGraph):
        self.graph_query = GraphQuery(graph)
        self.graph = graph

    def find_causal_links(self, current_service: str, memories: List[Memory]) -> List[Tuple[Memory, float, str]]:
        results = []
        for memory in memories:
            if memory.service == current_service:
                continue
            
            source_node = f"service:{current_service}"
            target_node = f"service:{memory.service}"
            
            path = self.graph_query.explain_path(source_node, target_node)
            if not path:
                path = self.graph_query.explain_path(target_node, source_node)
                
            if path:
                score = 1.0 / len(path)
                path_str = " -> ".join([p.replace("service:", "") for p in path if p.startswith("service:")])
                explanation = f"Hidden dependency path found: {path_str}"
                results.append((memory, score, explanation))
                
        return sorted(results, key=lambda x: x[1], reverse=True)
