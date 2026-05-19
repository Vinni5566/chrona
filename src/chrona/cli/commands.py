import json
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from chrona.scanner.repo_scanner import RepoScanner
from chrona.graph.graph_builder import GraphBuilder
from chrona.graph.graph_store import GraphStore
from chrona.graph.graph_query import GraphQuery
from chrona.graph.graph_visualizer import GraphVisualizer
from chrona.memory.memory_service import MemoryService
from chrona.schemas.memory import Memory
from chrona.services.incident_service import IncidentService
from chrona.services.replay_service import ReplayService
from chrona.services.report_service import ReportService

app = typer.Typer(help="Chrona - Temporal Memory Reliability Layer")
console = Console()

@app.command()
def scan(path: str = typer.Argument(".", help="Path to repository to scan")):
    """Scan a repository and build a graph memory."""
    console.print(f"[bold green]Scanning repository at:[/bold green] {path}")
    scanner = RepoScanner(path)
    facts = scanner.scan()
    console.print(f"Scanned {facts['files_scanned']} files.")
    
    builder = GraphBuilder()
    builder.build_from_facts(facts)
    graph = builder.get_graph()
    
    store = GraphStore("data/graph")
    store.save(graph)
    
    console.print(f"[bold green]Graph built with {len(graph.nodes)} nodes and {len(graph.edges)} edges.[/bold green]")

@app.command()
def ingest_incident(path: str = typer.Argument(..., help="Path to incident JSON file")):
    """Ingest a new incident and update memory."""
    console.print(f"[bold green]Ingesting incident from:[/bold green] {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    memory_data = data.get("memory")
    if not memory_data:
        console.print("[red]No memory object found in incident JSON.[/red]")
        return
        
    memory_data["id"] = f"mem-{data['id']}"
    memory_data["incident_id"] = data["id"]
    if "infra_version" not in memory_data and "metadata" in data:
        memory_data["infra_version"] = data["metadata"].get("infra_version")
        
    memory = Memory(**memory_data)
    
    memory_service = MemoryService("data/memories")
    memory_service.store_memory(memory)
    
    console.print(f"[bold green]Successfully stored memory for incident {data['id']}[/bold green]")

@app.command()
def ask(query: str = typer.Argument(..., help="Query or incident description")):
    """Ask Chrona to analyze an incident query."""
    console.print(f"[bold blue]Incident Analysis[/bold blue]\n")
    
    service = IncidentService()
    results = service.analyze_query(query)
    
    store = GraphStore("data/graph")
    graph_obj = store.load()
    query_graph = GraphQuery(graph_obj)
    
    from chrona.graph.service_mapper import ServiceMapper
    resolved_sources = ServiceMapper.resolve_query_terms(query, graph_obj)
    source_service = resolved_sources[0] if resolved_sources else None
                
    table = Table(title="Retrieved Memories")
    table.add_column("Memory ID", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Final Score", justify="right", style="green")
    table.add_column("Explanation")
    
    target_service = None

    for res in results["memories"]:
        mem = res["memory"]
        score = res["score"]
        causal = res["causal_links"]
        
        resolved_targets = ServiceMapper.resolve_query_terms(mem.service, graph_obj)
        if score.status in ["fresh", "historical_useful"] and not target_service:
            if resolved_targets:
                target_service = resolved_targets[0]
            else:
                target_service = f"service:{mem.service}"
            
        status_color = "green" if score.status == "fresh" else "yellow" if score.status == "historical_useful" else "red"
        
        explanation = score.explanation
        if causal:
            explanation += "\n[bold yellow]Causal:[/bold yellow] " + causal[0]
            
        table.add_row(
            mem.id, 
            f"[{status_color}]{score.status}[/{status_color}]", 
            f"{score.final_score:.2f}",
            explanation
        )
        
    console.print(table)
    
    llm = results["llm_response"]
    console.print("\n[bold]Likely root cause:[/bold]")
    console.print(llm["likely_root_cause"])
    
    console.print("\n[bold]Evidence:[/bold]")
    for e in llm["evidence"]:
        console.print(f"- {e}")
        
    console.print("\n[bold]Suggested Remediation:[/bold]")
    for s in llm["suggested_remediation"]:
        console.print(f"- {s}")
        
    console.print(f"\n[bold]Risk Level:[/bold] {llm['risk_level']}")
    console.print(f"[bold]Human Approval Required:[/bold] {llm['human_approval_required']}")

    project_name = graph_obj.graph.get("project_name") or graph_obj.graph.get("name") or "unknown-project"
    console.print(f"\n[bold]Scanned Project:[/bold] {project_name}")
    
    graph_region_str = "No dependency path detected"
    paths_to_suggest = []
    
    if source_service and target_service:
        path = query_graph.explain_path(source_service, target_service)
        if path:
            clean_path = [p.replace("service:", "").replace("dependency:node:", "").replace("dependency:python:", "") for p in path]
            graph_region_str = " -> ".join(clean_path)
            src_name = source_service.replace("service:", "")
            tgt_name = target_service.replace("service:", "")
            paths_to_suggest.append(f"chrona graph-path {src_name} {tgt_name} --visualize")
        else:
            region_nodes = query_graph.get_related_region(source_service, depth=2)
            if target_service not in region_nodes:
                target_region = query_graph.get_related_region(target_service, depth=2)
                region_nodes.extend(target_region)
                
            region_nodes = list(set(region_nodes))
            # Sort by node degree (connectivity) to get the most relevant ones
            try:
                region_nodes.sort(key=lambda n: query_graph.graph.degree(n), reverse=True)
            except Exception:
                pass
            
            # Limit to top 5
            region_nodes = region_nodes[:5]
            
            clean_nodes = [n.replace("service:", "").replace("dependency:node:", "").replace("dependency:python:", "") for n in region_nodes]
            if clean_nodes:
                graph_region_str = ", ".join(clean_nodes)
                console.print(f"\n[bold]Related Region:[/bold]\n{graph_region_str}")
                graph_region_str = ""
            
    if graph_region_str:
        console.print(f"\n[bold]Graph Region:[/bold]\n{graph_region_str}")
    
    for path_cmd in paths_to_suggest:
        console.print(f"\n[dim]Run this to visualize the path:[/dim]\n{path_cmd}")
    
    decision = results["routing"]
    if getattr(decision, "provider", "") == "mock-router" or "mock" in decision.selected_model.lower():
        routing_str = f"{decision.selected_model} via mock-router fallback"
    else:
        routing_str = f"{decision.selected_model} via cascadeflow"
        
    console.print(f"\n[bold]Routing:[/bold]\n{routing_str}")

@app.command()
def demo(
    query: str = typer.Option("checkout latency spike after deployment", help="Query to run for demo"),
    repo_path: str = typer.Option("../microservices-demo", help="Path to repository to scan")
):
    """Run an end-to-end demo of Chrona."""
    console.print("[bold magenta]=== Starting Chrona End-to-End Demo ===[/bold magenta]\n")
    
    console.print(f"[bold yellow]Step 1: Scanning Repository at {repo_path}[/bold yellow]")
    scan(repo_path)
    
    console.print("\n[bold yellow]Step 2: Asking Question[/bold yellow]")
    console.print(f"Query: [cyan]{query}[/cyan]\n")
    ask(query)
    
    console.print("\n[bold magenta]=== Demo Complete ===[/bold magenta]")

@app.command()
def replay(incident_id: str = typer.Argument(..., help="Incident ID to replay")):
    """Replay a past incident analysis."""
    console.print(f"[bold green]Replaying incident:[/bold green] {incident_id}")
    console.print("[yellow]Naive retrieval would just fetch the latest matching term...[/yellow]")
    console.print("[green]Chrona retrieval flow running...[/green]")
    service = ReplayService()
    service.replay(incident_id) 
    
    ask("checkout API latency spiked but Redis looks healthy")

@app.command()
def route_stats():
    """Show routing statistics for cascadeflow."""
    console.print("[bold green]Displaying routing stats...[/bold green]")
    service = ReportService()
    stats = service.get_route_stats()
    console.print(Panel(json.dumps(stats, indent=2), title="Cascadeflow Routing Stats"))

@app.command()
def stale_report():
    """Generate a report of stale or dangerous memories."""
    console.print("[bold green]Generating stale memory report...[/bold green]")
    service = ReportService()
    report = service.generate_stale_report()
    
    table = Table(title="Stale Memory Report")
    table.add_column("Memory ID")
    table.add_column("Service")
    table.add_column("Status")
    table.add_column("Reason")
    
    for r in report:
        color = "red" if r["status"] == "stale" else "green"
        table.add_row(r["id"], r["service"], f"[{color}]{r['status']}[/{color}]", r["reason"])
        
    console.print(table)

@app.command()
def graph(
    visualize: bool = typer.Option(False, "--visualize", help="Generate HTML visualization"),
    open_browser: bool = typer.Option(False, "--open", help="Open generated HTML in browser"),
    output: str = typer.Option("data/graph/chrona_graph.html", "--output", help="Output path for HTML")
):
    """Show stats about the current graph memory."""
    console.print("[bold green]Displaying graph memory stats...[/bold green]")
    store = GraphStore("data/graph")
    graph_obj = store.load()
    console.print(f"Nodes: {len(graph_obj.nodes)}")
    console.print(f"Edges: {len(graph_obj.edges)}")
    
    if visualize:
        try:
            visualizer = GraphVisualizer()
            path = visualizer.generate_html(output_path=output)
            console.print(f"\n[bold green]Visualization generated locally:[/bold green] {path}")
            console.print("No graph data was sent externally.")
            if open_browser:
                visualizer.open_in_browser(path)
        except Exception as e:
            console.print(f"[bold red]Error generating visualization:[/bold red] {str(e)}")

@app.command()
def graph_path(
    source: str = typer.Argument(..., help="Source node (e.g., checkout-api)"),
    target: str = typer.Argument(..., help="Target node (e.g., redis)"),
    visualize: bool = typer.Option(False, "--visualize", help="Generate HTML visualization"),
    open_browser: bool = typer.Option(False, "--open", help="Open generated HTML in browser")
):
    """Visualize a dependency path between two services."""
    store = GraphStore("data/graph")
    graph_obj = store.load()
    query = GraphQuery(graph_obj)
    
    src_node = f"service:{source}" if not source.startswith("service:") else source
    tgt_node = f"service:{target}" if not target.startswith("service:") else target
    
    path = query.explain_path(src_node, tgt_node)
    if not path:
        console.print(f"[bold red]No path found between {src_node} and {tgt_node}[/bold red]")
        return
        
    console.print(f"[bold green]Path found:[/bold green] {' -> '.join(path)}")
    
    if visualize:
        try:
            visualizer = GraphVisualizer()
            output_file = f"data/graph/chrona_path_{source}_{target}.html"
            out_path = visualizer.generate_html(output_path=output_file, highlight_path=path)
            console.print(f"\n[bold green]Visualization generated locally:[/bold green] {out_path}")
            console.print("No graph data was sent externally.")
            if open_browser:
                visualizer.open_in_browser(out_path)
        except Exception as e:
            console.print(f"[bold red]Error generating visualization:[/bold red] {str(e)}")

if __name__ == "__main__":
    app()
