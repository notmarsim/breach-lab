"""Main entry point for the `breachlab` CLI."""

from __future__ import annotations

import subprocess
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from cli.commands.scenario import scenario_app
from cli.commands.snapshot import snapshot_app
from orchestrator.config import get_project_root, list_profiles, load_config, load_profile
from orchestrator.docker_manager import DockerManager
from orchestrator.health_manager import HealthManager
from orchestrator.network_manager import NetworkManager
from orchestrator.recovery_manager import RecoveryManager
from orchestrator.resource_manager import ResourceManager
from synthetic_data.generator import export_dataset
from validation.isolation import IsolationValidator

app = typer.Typer(
    name="breachlab",
    help="BreachLab — Enterprise Pentesting Training Environment CLI.",
    no_args_is_help=True,
)
app.add_typer(scenario_app, name="scenario")
app.add_typer(snapshot_app, name="snapshot")

console = Console()


@app.command()
def doctor(
    skip_host_routes: bool = typer.Option(
        False, "--skip-host-routes", help="Skip checking host interface/routing overlaps."
    ),
) -> None:
    """Run environment, network, resource, and isolation diagnostics."""
    hm = HealthManager(get_project_root())
    results = hm.run_doctor(check_host_routes=not skip_host_routes)

    table = Table(title="BreachLab Doctor Diagnostics")
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    all_ok = True
    for res in results:
        status = "[green]PASS[/green]" if res.passed else "[red]FAIL[/red]"
        if not res.passed:
            all_ok = False
        table.add_row(res.name, status, res.detail)

    console.print(table)
    if not all_ok:
        raise typer.Exit(code=1)


@app.command("isolation-check")
def isolation_check() -> None:
    """Verify fail-closed isolation policies (compose & host firewall)."""
    root = get_project_root()
    validator = IsolationValidator(root)
    report = validator.validate_compose()
    nft_ok, nft_msg = validator.check_linux_nftables()

    for warn in report.warnings:
        console.print(f"[yellow]Warning:[/yellow] {warn}")
    for viol in report.violations:
        console.print(f"[red]Violation:[/red] {viol}")

    console.print(f"Firewall check: {'[green]OK[/green]' if nft_ok else '[red]FAIL[/red]'} - {nft_msg}")

    if not report.passed or not nft_ok:
        console.print("[red]Isolation check FAILED (fail-closed policy).[/red]")
        raise typer.Exit(code=1)
    console.print("[green]Isolation check PASSED.[/green]")


@app.command()
def validate() -> None:
    """Validate configuration files, profiles, networks, and compose manifest."""
    root = get_project_root()
    try:
        cfg = load_config(root)
        profiles = list_profiles(root)
        for p in profiles:
            load_profile(p, root)
    except Exception as exc:
        console.print(f"[red]Configuration validation failed:[/red] {exc}")
        raise typer.Exit(code=1)

    conflicts = NetworkManager(root).validate_topology(check_host_routes=False)
    iso = IsolationValidator(root).validate_compose()
    if conflicts or not iso.passed:
        for c in conflicts:
            console.print(f"[red]Network conflict:[/red] {c.network_name}: {c.reason}")
        for v in iso.violations:
            console.print(f"[red]Isolation violation:[/red] {v}")
        raise typer.Exit(code=1)

    console.print(
        f"[green]Validation passed.[/green] Version={cfg.version}, Profiles={len(profiles)}"
    )


@app.command()
def start(
    profile: str = typer.Option(
        "balanced",
        "--profile",
        "-p",
        help="Resource profile: minimal, web, api, web-api, infrastructure, privesc, balanced, full.",
    ),
    build: bool = typer.Option(False, "--build", help="Build container images before starting."),
    force: bool = typer.Option(False, "--force", help="Proceed despite resource warnings."),
) -> None:
    """Start the BreachLab training environment (fail-closed isolation enforced)."""
    root = get_project_root()
    iso = IsolationValidator(root).validate_compose()
    if not iso.passed:
        for v in iso.violations:
            console.print(f"[red]Isolation violation:[/red] {v}")
        console.print("[red]Aborting start: fail-closed isolation check failed.[/red]")
        raise typer.Exit(code=1)

    conflicts = NetworkManager(root).validate_topology(check_host_routes=True)
    if conflicts:
        for c in conflicts:
            console.print(f"[red]Network conflict:[/red] {c.network_name}: {c.reason}")
        raise typer.Exit(code=1)

    try:
        assessment = ResourceManager(root).assess_profile(profile)
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)

    for w in assessment.warnings:
        console.print(f"[yellow]Resource warning:[/yellow] {w}")
    if not assessment.fits and not force:
        console.print(
            f"[red]Insufficient host resources for '{profile}'.[/red] "
            f"Recommended: '{assessment.recommended_profile}' (or pass --force)."
        )
        raise typer.Exit(code=1)

    docker = DockerManager(root)
    if not docker.daemon_ready():
        console.print("[red]Docker daemon is not running or inaccessible.[/red]")
        raise typer.Exit(code=1)

    dataset_file = root / "synthetic_data" / "dataset.json"
    if not dataset_file.exists():
        export_dataset(root / "synthetic_data")

    res = docker.up(profiles=assessment.profile.compose_profiles, build=build)
    if not res.ok:
        console.print(f"[red]Failed to start BreachLab:[/red]\n{res.stderr}")
        raise typer.Exit(code=res.returncode or 1)
    console.print(f"[green]BreachLab started[/green] with profile '[bold]{profile}[/bold]'.")


@app.command()
def stop(
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Profile to stop."),
) -> None:
    """Stop all running BreachLab containers."""
    root = get_project_root()
    profiles = load_profile(profile, root).compose_profiles if profile else None
    res = DockerManager(root).down(profiles=profiles)
    if not res.ok:
        console.print(f"[red]Failed to stop BreachLab:[/red]\n{res.stderr}")
        raise typer.Exit(code=res.returncode or 1)
    console.print("[green]BreachLab stopped.[/green]")


@app.command()
def restart(
    profile: str = typer.Option("balanced", "--profile", "-p", help="Resource profile to restart."),
) -> None:
    """Restart the BreachLab environment."""
    stop(profile=profile)
    start(profile=profile, build=False, force=False)


@app.command()
def status() -> None:
    """Show running containers and resource summary."""
    root = get_project_root()
    docker = DockerManager(root)
    if not docker.daemon_ready():
        console.print("[yellow]Docker daemon is not reachable.[/yellow]")
        raise typer.Exit(code=1)

    entries = docker.ps()
    if not entries:
        console.print("No BreachLab containers are currently running.")
        return

    table = Table(title="BreachLab Container Status")
    table.add_column("Service", style="cyan")
    table.add_column("State")
    table.add_column("Status")
    for entry in entries:
        table.add_row(
            str(entry.get("Service", entry.get("Name", "unknown"))),
            str(entry.get("State", "unknown")),
            str(entry.get("Status", "")),
        )
    console.print(table)


@app.command()
def logs(
    service: Optional[str] = typer.Option(None, "--service", "-s", help="Specific service name."),
    tail: int = typer.Option(100, "--tail", "-n", help="Number of lines to display."),
) -> None:
    """View container logs."""
    res = DockerManager(get_project_root()).logs(service=service, tail=tail)
    if not res.ok:
        console.print(f"[red]Error fetching logs:[/red] {res.stderr}")
        raise typer.Exit(code=1)
    console.print(res.stdout or "(no logs)")


@app.command()
def reset(
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Single target service to reset."),
    preserve_progress: bool = typer.Option(
        True, "--preserve-progress/--clear-progress", help="Keep or clear user progress."
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Reset a single target or the entire lab environment."""
    scope = f"target '{target}'" if target else "ENTIRE lab environment"
    if not yes:
        typer.confirm(f"Are you sure you want to reset {scope}?", abort=True)

    mgr = RecoveryManager(get_project_root())
    ok, msg = mgr.reset_target(target) if target else mgr.reset_global(preserve_progress=preserve_progress)
    if not ok:
        console.print(f"[red]Reset failed:[/red] {msg}")
        raise typer.Exit(code=1)
    console.print(f"[green]{msg}[/green]")


@app.command()
def cleanup(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Remove stopped lab containers, unused lab networks, and temporary artifacts."""
    if not yes:
        typer.confirm("Remove stopped BreachLab containers and unused volumes?", abort=True)
    res = DockerManager(get_project_root()).down(remove_volumes=True)
    if not res.ok:
        console.print(f"[red]Cleanup failed:[/red] {res.stderr}")
        raise typer.Exit(code=1)
    console.print("[green]Cleanup completed.[/green]")


@app.command()
def install() -> None:
    """Run the idempotent Linux installer (`install.sh`)."""
    script = get_project_root() / "install.sh"
    if not script.exists():
        console.print(f"[red]Installer not found:[/red] {script}")
        raise typer.Exit(code=1)
    proc = subprocess.run(["bash", str(script)], check=False)
    raise typer.Exit(code=proc.returncode)


@app.command()
def update() -> None:
    """Pull repository updates and refresh configuration."""
    root = get_project_root()
    proc = subprocess.run(["git", "pull", "--ff-only"], cwd=str(root), check=False)
    if proc.returncode != 0:
        console.print("[red]Git pull failed.[/red]")
        raise typer.Exit(code=proc.returncode)
    console.print("[green]Repository updated. Run `breachlab validate` to verify.[/green]")


@app.command()
def uninstall(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Run the uninstaller (`uninstall.sh`)."""
    if not yes:
        typer.confirm("Uninstall BreachLab containers, networks, and CLI?", abort=True)
    script = get_project_root() / "uninstall.sh"
    if not script.exists():
        console.print(f"[red]Uninstaller not found:[/red] {script}")
        raise typer.Exit(code=1)
    proc = subprocess.run(["bash", str(script)], check=False)
    raise typer.Exit(code=proc.returncode)


if __name__ == "__main__":
    app()
