"""Scenario subcommands for `breachlab scenario`."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from orchestrator.config import get_project_root
from orchestrator.scenario_manager import ScenarioManager

scenario_app = typer.Typer(help="Create, list, save, load, and inspect scenarios.")
console = Console()


@scenario_app.command("new")
def scenario_new(
    seed: Optional[int] = typer.Option(None, "--seed", help="Deterministic seed for reproducibility."),
    profile: str = typer.Option("balanced", "--profile", "-p", help="Resource profile."),
    mode: str = typer.Option("learning", "--mode", "-m", help="Training mode."),
    difficulty: str = typer.Option("medium", "--difficulty", "-d", help="Difficulty tier."),
    save: bool = typer.Option(True, "--save/--no-save", help="Save generated scenario to scenarios/."),
) -> None:
    """Generate a new reproducible scenario."""
    mgr = ScenarioManager(get_project_root())
    try:
        manifest = mgr.generate(seed=seed, profile=profile, mode=mode, difficulty=difficulty)
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)

    if save:
        path = mgr.save(manifest)
        console.print(f"[green]Scenario created and saved:[/green] {manifest.scenario_id} ({path})")
    else:
        mgr.set_active(manifest)
        console.print(f"[green]Scenario created (active):[/green] {manifest.scenario_id}")

    console.print(
        f"Seed: [bold]{manifest.seed}[/bold] | Profile: {manifest.profile} | "
        f"Mode: {manifest.mode} | Difficulty: {manifest.difficulty}"
    )


@scenario_app.command("list")
def scenario_list() -> None:
    """List all saved scenarios."""
    mgr = ScenarioManager(get_project_root())
    items = mgr.list_scenarios()
    if not items:
        console.print("No saved scenarios found. Run `breachlab scenario new` to create one.")
        return

    table = Table(title="Saved BreachLab Scenarios")
    table.add_column("ID", style="cyan")
    table.add_column("Seed")
    table.add_column("Profile")
    table.add_column("Mode")
    table.add_column("Difficulty")
    for item in items:
        table.add_row(item.scenario_id, str(item.seed), item.profile, item.mode, item.difficulty)
    console.print(table)


@scenario_app.command("save")
def scenario_save(name: str = typer.Argument(..., help="Filename (without .yaml) to save active scenario.")) -> None:
    """Save the currently active scenario under a custom name."""
    mgr = ScenarioManager(get_project_root())
    active = mgr.get_active()
    if not active:
        console.print("[red]Error:[/red] No active scenario. Run `breachlab scenario new` first.")
        raise typer.Exit(code=1)
    path = mgr.save(active, name=name)
    console.print(f"[green]Saved active scenario to:[/green] {path}")


@scenario_app.command("load")
def scenario_load(name_or_id: str = typer.Argument(..., help="Scenario name or ID to load.")) -> None:
    """Load a saved scenario and set it as active."""
    mgr = ScenarioManager(get_project_root())
    try:
        manifest = mgr.load(name_or_id)
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)
    console.print(f"[green]Loaded scenario:[/green] {manifest.scenario_id} (seed={manifest.seed})")


@scenario_app.command("info")
def scenario_info(
    name_or_id: Optional[str] = typer.Argument(None, help="Scenario ID/name (defaults to active).")
) -> None:
    """Display details about a scenario (hides spoilers in blackbox mode)."""
    mgr = ScenarioManager(get_project_root())
    try:
        manifest = mgr.load(name_or_id) if name_or_id else mgr.get_active()
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)

    if not manifest:
        console.print("No active scenario. Specify a scenario ID or run `breachlab scenario new`.")
        raise typer.Exit(code=1)

    console.print(f"[bold]Scenario:[/bold] {manifest.scenario_id}")
    console.print(f"Seed: {manifest.seed} | Catalog: {manifest.catalog_version}")
    console.print(f"Profile: {manifest.profile} | Mode: {manifest.mode} | Difficulty: {manifest.difficulty}")
    console.print(f"Domain: {manifest.domain}")
    if manifest.mode == "blackbox":
        console.print("[yellow]Black Box mode active: internal topology and objectives are hidden.[/yellow]")
    else:
        console.print(f"Services: {', '.join(manifest.services)}")
        console.print(f"Objectives: {len(manifest.objectives)}")
