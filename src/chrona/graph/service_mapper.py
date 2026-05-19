import re
import networkx as nx
from typing import Dict, List

class ServiceMapper:
    @staticmethod
    def normalize_name(name: str) -> str:
        if not name:
            return ""
        # Strip prefixes like service: or dependency:
        if ":" in name:
            name = name.split(":", 1)[1]
        name = name.lower()
        # Remove terms
        for term in ["service", "api", "svc"]:
            name = name.replace(term, "")
        # Remove special characters
        for char in ["_", "-", " "]:
            name = name.replace(char, "")
        return name

    @staticmethod
    def build_alias_map(graph: nx.DiGraph) -> Dict[str, List[str]]:
        alias_map = {}
        for node, data in graph.nodes(data=True):
            node_type = data.get("type")
            if node_type in ["service", "database", "repo"]:
                name = data.get("name") or node
                norm_name = ServiceMapper.normalize_name(name)
                if norm_name and norm_name != "repositoryroot" and norm_name != "root":
                    if norm_name not in alias_map:
                        alias_map[norm_name] = []
                    alias_map[norm_name].append(node)
        return alias_map

    @staticmethod
    def resolve_query_terms(query: str, graph: nx.DiGraph) -> List[str]:
        alias_map = ServiceMapper.build_alias_map(graph)
        # Tokenize query
        words = re.findall(r'\b[a-zA-Z0-9_-]+\b', query.lower())
        resolved = set()
        
        for word in words:
            norm_word = ServiceMapper.normalize_name(word)
            if not norm_word:
                continue
                
            for norm_alias, nodes in alias_map.items():
                # Check for exact match, containment, or overlap
                if norm_word == norm_alias or norm_word in norm_alias or norm_alias in norm_word:
                    for node in nodes:
                        resolved.add(node)
        return list(resolved)
