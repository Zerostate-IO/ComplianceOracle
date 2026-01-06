"""CLI for Compliance Oracle - fetch, validate, and manage framework data."""

import asyncio
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from compliance_oracle.frameworks.manager import FrameworkManager
from compliance_oracle.rag.search import ControlSearcher

console = Console()


@click.group()
def main() -> None:
    """Compliance Oracle CLI - manage compliance framework data."""
    pass


@main.command()
@click.option(
    "--framework",
    "-f",
    type=click.Choice(["all", "nist-csf-2.0", "nist-800-53-r5"]),
    default="all",
    help="Framework to fetch (default: all)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory for framework data",
)
def fetch(framework: str, output_dir: Path | None) -> None:
    """Fetch framework data from NIST CPRT."""
    asyncio.run(_fetch(framework, output_dir))


async def _fetch(framework: str, output_dir: Path | None) -> None:
    """Async implementation of fetch command."""
    import httpx

    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent / "data" / "frameworks"

    output_dir.mkdir(parents=True, exist_ok=True)

    frameworks_to_fetch = []
    if framework == "all":
        frameworks_to_fetch = ["nist-csf-2.0", "nist-800-53-r5"]
    else:
        frameworks_to_fetch = [framework]

    # NIST CPRT API endpoints
    endpoints = {
        "nist-csf-2.0": "https://csrc.nist.gov/extensions/nudp/services/json/nudp/framework/version/csf_2_0_0/export/json?element=all",
        "nist-800-53-r5": "https://csrc.nist.gov/extensions/nudp/services/json/nudp/framework/version/sp_800_53_5_1_1/export/json?element=all",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        for fw_id in frameworks_to_fetch:
            url = endpoints.get(fw_id)
            if not url:
                console.print(f"[red]Unknown framework: {fw_id}[/red]")
                continue

            console.print(f"[blue]Fetching {fw_id}...[/blue]")

            try:
                response = await client.get(url)
                response.raise_for_status()

                output_file = output_dir / f"{fw_id}.json"
                output_file.write_text(response.text)

                console.print(f"[green]Saved to {output_file}[/green]")
            except httpx.HTTPError as e:
                console.print(f"[red]Failed to fetch {fw_id}: {e}[/red]")


@main.command()
@click.option(
    "--framework",
    "-f",
    type=click.Choice(["all", "nist-csf-2.0", "nist-800-53-r5"]),
    default="all",
    help="Framework to validate",
)
def validate(framework: str) -> None:
    """Validate framework data files."""
    asyncio.run(_validate(framework))


async def _validate(framework: str) -> None:
    """Async implementation of validate command."""
    manager = FrameworkManager()

    frameworks = await manager.list_frameworks()

    table = Table(title="Framework Validation")
    table.add_column("Framework ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Status", style="yellow")
    table.add_column("Controls", justify="right", style="green")

    for fw in frameworks:
        if framework != "all" and fw.id != framework:
            continue

        status_icon = "[green]" if fw.status.value == "active" else "[yellow]"
        status = f"{status_icon}{fw.status.value}[/]"

        table.add_row(
            fw.id,
            fw.name,
            status,
            str(fw.control_count) if fw.control_count > 0 else "[dim]N/A[/dim]",
        )

    console.print(table)


@main.command()
def status() -> None:
    """Show current status of Compliance Oracle."""
    asyncio.run(_status())


async def _status() -> None:
    """Async implementation of status command."""
    console.print("[bold]Compliance Oracle Status[/bold]\n")

    # Check frameworks
    manager = FrameworkManager()
    frameworks = await manager.list_frameworks()

    console.print("[cyan]Frameworks:[/cyan]")
    for fw in frameworks:
        if fw.status.value == "active":
            console.print(f"  [green]✓[/green] {fw.id}: {fw.control_count} controls")
        else:
            console.print(f"  [yellow]○[/yellow] {fw.id}: Not installed")

    # Check vector store
    console.print("\n[cyan]Vector Store:[/cyan]")
    searcher = ControlSearcher()

    for fw in frameworks:
        if fw.status.value == "active":
            indexed = await searcher.is_indexed(fw.id)
            count = await searcher.get_indexed_count(fw.id) if indexed else 0
            if indexed:
                console.print(f"  [green]✓[/green] {fw.id}: {count} controls indexed")
            else:
                console.print(f"  [yellow]○[/yellow] {fw.id}: Not indexed")


@main.command()
@click.option(
    "--framework",
    "-f",
    type=click.Choice(["all", "nist-csf-2.0", "nist-800-53-r5"]),
    default="all",
    help="Framework to index",
)
def index(framework: str) -> None:
    """Index framework controls into vector store for semantic search."""
    asyncio.run(_index(framework))


async def _index(framework: str) -> None:
    """Async implementation of index command."""
    manager = FrameworkManager()
    searcher = ControlSearcher(framework_manager=manager)

    frameworks = await manager.list_frameworks()

    for fw in frameworks:
        if framework != "all" and fw.id != framework:
            continue

        if fw.status.value != "active":
            console.print(f"[yellow]Skipping {fw.id} (not installed)[/yellow]")
            continue

        console.print(f"[blue]Indexing {fw.id}...[/blue]")

        count = await searcher.index_framework(fw.id)
        console.print(f"[green]Indexed {count} controls from {fw.id}[/green]")


@main.command()
@click.argument("query")
@click.option(
    "--framework",
    "-f",
    type=str,
    default=None,
    help="Limit search to specific framework",
)
@click.option(
    "--limit",
    "-n",
    type=int,
    default=10,
    help="Maximum number of results",
)
def search(query: str, framework: str | None, limit: int) -> None:
    """Search for controls matching a query."""
    asyncio.run(_search(query, framework, limit))


async def _search(query: str, framework: str | None, limit: int) -> None:
    """Async implementation of search command."""
    searcher = ControlSearcher()

    console.print(f"[blue]Searching for: {query}[/blue]\n")

    results = await searcher.search(query, framework_id=framework, limit=limit)

    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    table = Table(title=f"Search Results ({len(results)} found)")
    table.add_column("Control ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Framework", style="yellow")
    table.add_column("Score", justify="right", style="green")

    for result in results:
        table.add_row(
            result.control_id,
            result.control_name[:50] + "..."
            if len(result.control_name) > 50
            else result.control_name,
            result.framework_id,
            f"{result.relevance_score:.2f}",
        )

    console.print(table)


@main.command()
@click.argument("control_id")
@click.option(
    "--framework",
    "-f",
    type=str,
    default="nist-csf-2.0",
    help="Framework ID",
)
def show(control_id: str, framework: str) -> None:
    """Show details for a specific control."""
    asyncio.run(_show(control_id, framework))


async def _show(control_id: str, framework: str) -> None:
    """Async implementation of show command."""
    manager = FrameworkManager()

    control = await manager.get_control_details(framework, control_id)

    if not control:
        console.print(f"[red]Control {control_id} not found in {framework}[/red]")
        return

    console.print(f"[bold cyan]{control.id}[/bold cyan] - {control.name}\n")
    console.print(f"[bold]Framework:[/bold] {control.framework_id}")
    console.print(f"[bold]Function:[/bold] {control.function_id} ({control.function_name})")
    console.print(f"[bold]Category:[/bold] {control.category_id} ({control.category_name})")
    console.print(f"\n[bold]Description:[/bold]\n{control.description}")

    if control.implementation_examples:
        console.print("\n[bold]Implementation Examples:[/bold]")
        for example in control.implementation_examples:
            console.print(f"  • {example}")

    if control.informative_references:
        console.print("\n[bold]Informative References:[/bold]")
        for ref in control.informative_references[:5]:  # Limit to 5
            console.print(f"  • {ref}")
        if len(control.informative_references) > 5:
            console.print(f"  ... and {len(control.informative_references) - 5} more")

    if control.related_controls:
        console.print(f"\n[bold]Related Controls:[/bold] {', '.join(control.related_controls)}")

    if control.mappings:
        console.print("\n[bold]Cross-Framework Mappings:[/bold]")
        for target_fw, refs in control.mappings.items():
            console.print(f"  {target_fw}:")
            for ref in refs:
                console.print(f"    • {ref}")


@main.command()
@click.option(
    "--framework",
    "-f",
    type=str,
    default=None,
    help="Clear only specific framework (clears all if not specified)",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt",
)
def clear(framework: str | None, yes: bool) -> None:
    """Clear indexed controls from vector store."""
    if not yes:
        if framework:
            msg = f"Clear all indexed controls for {framework}?"
        else:
            msg = "Clear ALL indexed controls?"
        if not click.confirm(msg):
            return

    asyncio.run(_clear(framework))


async def _clear(framework: str | None) -> None:
    """Async implementation of clear command."""
    searcher = ControlSearcher()

    count = await searcher.clear_index(framework)

    if framework:
        console.print(f"[green]Cleared {count} controls from {framework}[/green]")
    else:
        console.print(f"[green]Cleared {count} controls from vector store[/green]")


if __name__ == "__main__":
    main()
