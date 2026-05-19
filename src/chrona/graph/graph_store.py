import networkx as nx
import json
from pathlib import Path
from typing import Optional

class GraphStore:
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.graph_file = self.storage_dir / "memory_graph.json"

    def save(self, graph: nx.DiGraph):
        data = nx.node_link_data(graph, edges="links")
        with open(self.graph_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self) -> nx.DiGraph:
        if not self.graph_file.exists():
            return nx.DiGraph()
        with open(self.graph_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return nx.node_link_graph(data, edges="links")
