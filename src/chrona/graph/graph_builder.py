import networkx as nx
from typing import Dict, Any

class GraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_from_facts(self, repo_facts: Dict[str, Any]):
        repo_node_id = "repo:root"
        self.graph.add_node(repo_node_id, type="repo", name="Repository Root")
        if "project_name" in repo_facts:
            self.graph.graph["project_name"] = repo_facts["project_name"]

        # Add services
        for svc in repo_facts.get("services", []):
            svc_id = f"service:{svc}"
            self.graph.add_node(svc_id, type="service", name=svc)
            self.graph.add_edge(repo_node_id, svc_id, relation="contains", confidence=1.0)
            
            # Very naive assumption: services use databases like redis or postgres
            # if their name implies it or they commonly do (for MVP)
            if "redis" in svc.lower():
                self.graph.nodes[svc_id]["type"] = "database"

        # Add dependencies
        for lang, deps in repo_facts.get("dependencies", {}).items():
            for dep in deps:
                dep_id = f"dependency:{lang}:{dep}"
                self.graph.add_node(dep_id, type="dependency", name=dep)
                self.graph.add_edge(repo_node_id, dep_id, relation="depends_on", confidence=1.0)
                
        # Add k8s links
        for svc, deps in repo_facts.get("k8s_links", {}).items():
            svc_id = f"service:{svc}"
            # Ensure the source service exists
            if not self.graph.has_node(svc_id):
                self.graph.add_node(svc_id, type="service", name=svc)
                self.graph.add_edge(repo_node_id, svc_id, relation="contains", confidence=1.0)
            for dep in deps:
                dep_id = f"service:{dep}"
                # Ensure the target service exists
                if not self.graph.has_node(dep_id):
                    self.graph.add_node(dep_id, type="service", name=dep)
                    self.graph.add_edge(repo_node_id, dep_id, relation="contains", confidence=1.0)
                self.graph.add_edge(svc_id, dep_id, relation="depends_on", confidence=1.0)

    def get_graph(self) -> nx.DiGraph:
        return self.graph
