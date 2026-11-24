"""Health diagnostics and environment readiness checks (`breachlab doctor`)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from orchestrator.docker_manager import DockerManager
from orchestrator.network_manager import NetworkManager
from orchestrator.resource_manager import ResourceManager
from validation.isolation import IsolationValidator


@dataclass
class CheckResult:
    """Single diagnostic check outcome."""

    name: str
    passed: bool
    detail: str


class HealthManager:
    """Runs comprehensive pre-flight and runtime diagnostics."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.docker = DockerManager(project_root)
        self.networks = NetworkManager(project_root)
        self.resources = ResourceManager(project_root)
        self.isolation = IsolationValidator(project_root)

    def run_doctor(self, check_host_routes: bool = True) -> list[CheckResult]:
        """Run all environment, network, resource, and isolation checks."""
        results: list[CheckResult] = []

        docker_installed = self.docker.is_docker_installed()
        results.append(
            CheckResult(
                "Docker CLI",
                docker_installed,
                "Docker CLI is installed." if docker_installed else "Docker CLI not found in PATH.",
            )
        )

        daemon_up = self.docker.daemon_ready() if docker_installed else False
        results.append(
            CheckResult(
                "Docker Daemon",
                daemon_up,
                "Docker daemon is reachable." if daemon_up else "Docker daemon is not running or inaccessible.",
            )
        )

        conflicts = self.networks.validate_topology(check_host_routes=check_host_routes)
        results.append(
            CheckResult(
                "Network Topology",
                len(conflicts) == 0,
                "All 6 segmented subnets are valid and conflict-free."
                if not conflicts
                else "; ".join(f"{c.network_name}: {c.reason}" for c in conflicts),
            )
        )

        host = self.resources.get_host_resources()
        rec = self.resources.recommend_profile(host)
        results.append(
            CheckResult(
                "Host Resources",
                host.free_disk_gb >= 10.0 and host.total_ram_mb >= 2048,
                f"RAM: {host.total_ram_mb} MB (avail {host.available_ram_mb} MB), "
                f"CPUs: {host.cpu_count}, Disk free: {host.free_disk_gb} GB. Recommended profile: '{rec}'.",
            )
        )

        iso_report = self.isolation.validate_compose()
        results.append(
            CheckResult(
                "Static Isolation Policy",
                iso_report.passed,
                "Compose manifest passes all fail-closed isolation rules."
                if iso_report.passed
                else "; ".join(iso_report.violations),
            )
        )

        return results
