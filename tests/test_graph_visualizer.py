import os
import networkx as nx
from chrona.graph.graph_visualizer import GraphVisualizer

def test_graph_visualizer(tmp_path):
    import json
    from chrona.graph.graph_store import GraphStore
    
    # Create mock graph
    store = GraphStore(str(tmp_path))
    graph = nx.DiGraph()
    graph.add_node("service:test-api", type="service", name="test-api", status="fresh")
    graph.add_node("service:test-db", type="database", name="test-db", status="stale")
    graph.add_edge("service:test-api", "service:test-db", relation="depends_on")
    store.save(graph)
    
    # Mock the visualizer store
    visualizer = GraphVisualizer()
    visualizer.store = store
    
    output_html = str(tmp_path / "test_graph.html")
    result_path = visualizer.generate_html(output_path=output_html)
    
    assert os.path.exists(result_path)
    
    with open(result_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    assert "test-api" in html_content
    assert "test-db" in html_content
    assert "fake_secret_123" not in html_content  # Verifying no secrets
