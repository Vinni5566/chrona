import networkx as nx
from chrona.graph.service_mapper import ServiceMapper

def test_normalize_name():
    assert ServiceMapper.normalize_name("checkoutservice") == "checkout"
    assert ServiceMapper.normalize_name("payment-service") == "payment"
    assert ServiceMapper.normalize_name("redis-cart") == "rediscart"
    assert ServiceMapper.normalize_name("api-gateway") == "gateway"
    assert ServiceMapper.normalize_name("service:checkout-api") == "checkout"

def test_build_alias_map():
    graph = nx.DiGraph()
    graph.add_node("service:checkoutservice", type="service", name="checkoutservice")
    graph.add_node("service:paymentservice", type="service", name="paymentservice")
    graph.add_node("service:redis-cart", type="database", name="redis-cart")
    
    alias_map = ServiceMapper.build_alias_map(graph)
    
    assert "checkout" in alias_map
    assert "service:checkoutservice" in alias_map["checkout"]
    assert "payment" in alias_map
    assert "rediscart" in alias_map

def test_resolve_query_terms():
    graph = nx.DiGraph()
    graph.add_node("service:checkoutservice", type="service", name="checkoutservice")
    graph.add_node("service:paymentservice", type="service", name="paymentservice")
    graph.add_node("service:redis-cart", type="database", name="redis-cart")
    
    query = "checkout latency spike after deployment"
    resolved = ServiceMapper.resolve_query_terms(query, graph)
    assert "service:checkoutservice" in resolved
    
    query2 = "redis timeout"
    resolved2 = ServiceMapper.resolve_query_terms(query2, graph)
    assert "service:redis-cart" in resolved2
    
    query3 = "payment queue stuck"
    resolved3 = ServiceMapper.resolve_query_terms(query3, graph)
    assert "service:paymentservice" in resolved3
