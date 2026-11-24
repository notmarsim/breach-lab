"""Snapshot subcommands for `breachlab snapshot`."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from orchestrator.config import get_project_root
from orchestrator.recovery_manager import RecoveryManager

snapshot_app = typer.Typer(help="Create, list, and restore lab snapshots.")
console = Console()


@snapshot_app.command("create")
def snapshot_create(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Custom snapshot name."),
    include_progress: bool = typer.Option(
        True, "--include-progress/--exclude-progress", help="Include user progress in snapshot."
    ),
) -> None:
    """Create a consistent snapshot of lab state."""
    mgr = RecoveryManager(get_project_root())
    try:
        info = mgr.create_snapshot(name=name, include_progress=include_progress)
    except FileExistsError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)
    console.print(f"[green]Snapshot created:[/green] {info.name} ({info.path})")


@snapshot_app.command("list")
def snapshot_list() -> None:
    """List available snapshots."""
    mgr = RecoveryManager(get_project_root())
    items = mgr.list_snapshots()
    if not items:
        console.print("No snapshots found.")
        return

    table = Table(title="BreachLab Snapshots")
    table.add_column("Name", style="cyan")
    table.add_column("Created At")
    table.add_column("Includes Progress")
    for item in items:
        table.add_row(item.name, item.created_at, "Yes" if item.includes_progress else "No")
    console.print(table)


@snapshot_app.command("restore")
def snapshot_restore(
    name: str = typer.Argument(..., help="Snapshot name to restore."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Restore lab state from a named snapshot."""
    if not yes:
        typer.confirm(f"Restore snapshot '{name}'? Current lab state will be overwritten.", abort=True)
    mgr = RecoveryManager(get_project_root())
    try:
        info = mgr.restore_snapshot(name)
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)
    console.print(f"[green]Snapshot restored:[/green] {info.name}")
