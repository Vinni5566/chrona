import networkx as nx

class GraphQuery:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def explain_path(self, source: str, target: str) -> list[str]:
        if not (self.graph.has_node(source) and self.graph.has_node(target)):
            return []
        try:
            path = nx.shortest_path(self.graph, source, target)
            return path
        except nx.NetworkXNoPath:
            return []

    def get_related_region(self, node_id: str, depth: int = 2) -> list[str]:
        if not self.graph.has_node(node_id):
            return []
        related = set([node_id])
        current_level = [node_id]
        
        for _ in range(depth):
            next_level = []
            for n in current_level:
                neighbors = list(self.graph.successors(n)) + list(self.graph.predecessors(n))
                for neighbor in neighbors:
                    if neighbor not in related:
                        related.add(neighbor)
                        next_level.append(neighbor)
            current_level = next_level
            
        return list(related)
