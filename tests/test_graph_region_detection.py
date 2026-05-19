import networkx as nx
from chrona.graph.graph_query import GraphQuery
from chrona.graph.service_mapper import ServiceMapper

def test_related_region_fallback():
    graph = nx.DiGraph()
    # No direct path between them
    graph.add_node("service:checkoutservice", type="service", name="checkoutservice")
    graph.add_node("service:paymentservice", type="service", name="paymentservice")
    graph.add_node("service:redis-cart", type="database", name="redis-cart")
    
    graph.add_edge("repo:root", "service:checkoutservice")
    graph.add_edge("repo:root", "service:paymentservice")
    graph.add_edge("repo:root", "service:redis-cart")
    
    query = GraphQuery(graph)
    
    path = query.explain_path("service:checkoutservice", "service:redis-cart")
    assert not path # No direct path since they only share a root predecessor, but explain_path uses shortest_path (directed)
    
    # Check related region
    region = query.get_related_region("service:checkoutservice", depth=2)
    assert "service:checkoutservice" in region
    assert "repo:root" in region

def test_shortest_path_rendering():
    graph = nx.DiGraph()
    graph.add_node("service:checkoutservice", type="service", name="checkoutservice")
    graph.add_node("service:paymentservice", type="service", name="paymentservice")
    graph.add_node("service:redis-cart", type="database", name="redis-cart")
    
    graph.add_edge("service:checkoutservice", "service:paymentservice")
    graph.add_edge("service:paymentservice", "service:redis-cart")
    
    query = GraphQuery(graph)
    
    path = query.explain_path("service:checkoutservice", "service:redis-cart")
    assert path == ["service:checkoutservice", "service:paymentservice", "service:redis-cart"]
