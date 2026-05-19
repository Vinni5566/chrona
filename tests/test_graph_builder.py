import networkx as nx
from chrona.graph.graph_builder import GraphBuilder

def test_graph_builder():
    facts = {
        "services": ["checkout-api", "redis-cache"],
        "dependencies": {
            "python": ["requests", "fastapi"]
        }
    }
    
    builder = GraphBuilder()
    builder.build_from_facts(facts)
    graph = builder.get_graph()
    
    assert len(graph.nodes) == 5 # 1 repo + 2 services + 2 deps
    assert graph.has_node("service:redis-cache")
    assert graph.nodes["service:redis-cache"]["type"] == "database" # specific logic test
