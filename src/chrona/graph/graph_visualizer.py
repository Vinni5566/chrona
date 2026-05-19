import os
import webbrowser
from typing import Optional, List, Dict, Any
import networkx as nx
from pyvis.network import Network
from chrona.graph.graph_store import GraphStore
from chrona.graph.graph_query import GraphQuery

class GraphVisualizer:
    def __init__(self):
        self.store = GraphStore("data/graph")

    def color_node(self, node_type: str, status: Optional[str] = None) -> str:
        if status == "fresh":
            return "#4ade80" 
        elif status == "historical_useful":
            return "#facc15" 
        elif status == "stale":
            return "#f87171" 
        elif status == "dangerous":
            return "#991b1b" 
        elif status == "unknown":
            return "#9ca3af" 

        colors = {
            "repo": "#6b7280",
            "domain": "#a855f7",
            "service": "#3b82f6",
            "api": "#06b6d4",
            "database": "#f97316",
            "queue": "#eab308",
            "config": "#d1d5db",
            "incident": "#ffffff",
            "dependency": "#9ca3af",
        }
        return colors.get(node_type, "#9ca3af")

    def build_safe_label(self, node_data: Dict[str, Any]) -> str:
        name = node_data.get("name", "Unknown")
        node_type = node_data.get("type", "unknown")
        status = node_data.get("status")
        
        label = f"{name}\n({node_type})"
        if status:
            label += f"\n[{status}]"
        return label

    def generate_html(self, output_path: str = "data/graph/chrona_graph.html", highlight_path: Optional[List[str]] = None, max_nodes: int = 150) -> str:
        graph = self.store.load()
        
        if not graph or len(graph.nodes) == 0:
            raise ValueError("Graph is empty or missing. Please run 'chrona scan .' first.")

        nodes_to_keep = set()
        
        if highlight_path:
            for node in highlight_path:
                if graph.has_node(node):
                    nodes_to_keep.add(node)
                    nodes_to_keep.update(list(graph.successors(node))[:5])
                    nodes_to_keep.update(list(graph.predecessors(node))[:5])

        for node, data in graph.nodes(data=True):
            if len(nodes_to_keep) >= max_nodes:
                break
            n_type = data.get("type", "")
            if n_type in ["repo", "domain", "service", "database", "queue", "api", "incident"]:
                nodes_to_keep.add(node)
                
        if len(nodes_to_keep) < max_nodes:
            for node in graph.nodes:
                if len(nodes_to_keep) >= max_nodes:
                    break
                nodes_to_keep.add(node)

        subgraph = graph.subgraph(nodes_to_keep)
        
        net = Network(height="800px", width="100%", directed=True, bgcolor="#0f172a", font_color="#e2e8f0")
        
        # Make the graph more attractive and physics-based
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -150,
              "centralGravity": 0.02,
              "springLength": 100,
              "springConstant": 0.08
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 200
          },
          "edges": {
            "smooth": {
              "type": "continuous",
              "forceDirection": "none"
            }
          }
        }
        """)

        for node, data in subgraph.nodes(data=True):
            node_type = data.get("type", "unknown")
            status = data.get("status")
            
            size = 25
            if node_type in ["repo", "domain"]: size = 40
            elif node_type == "service": size = 30
            elif node_type == "incident": size = 20
            
            border_width = 1
            border_color = "#4b5563"
            
            if highlight_path and node in highlight_path:
                size += 10
                border_width = 4
                border_color = "#60a5fa"
                
            net.add_node(
                node, 
                label=self.build_safe_label(data), 
                title=f"Type: {node_type}",
                color={
                    "background": self.color_node(node_type, status),
                    "border": border_color,
                    "highlight": {"border": "#3b82f6", "background": "#93c5fd"}
                },
                size=size,
                borderWidth=border_width
            )

        for u, v, data in subgraph.edges(data=True):
            color = "#4b5563"
            width = 1
            if highlight_path and u in highlight_path and v in highlight_path:
                color = "#60a5fa"
                width = 3
                
            net.add_edge(u, v, title=data.get("relation", ""), color=color, width=width)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        net.save_graph(output_path)
        return output_path

    def open_in_browser(self, path: str) -> None:
        abs_path = os.path.abspath(path)
        webbrowser.open(f"file://{abs_path}")
