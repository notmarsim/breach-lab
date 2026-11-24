"""Host resource detection, profile recommendation, and budget checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import psutil

from orchestrator.config import ResourceProfile, list_profiles, load_profile


@dataclass
class HostResources:
    """Snapshot of host CPU, memory, and disk capacity."""

    total_ram_mb: int
    available_ram_mb: int
    cpu_count: int
    free_disk_gb: float


@dataclass
class ResourceAssessment:
    """Compatibility verdict for a selected resource profile."""

    profile: ResourceProfile
    host: HostResources
    fits: bool
    recommended_profile: str
    warnings: list[str]


class ResourceManager:
    """Detects host resources and recommends or validates lab profiles."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def get_host_resources(self) -> HostResources:
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage(str(self.project_root))
        return HostResources(
            total_ram_mb=int(vm.total // (1024 * 1024)),
            available_ram_mb=int(vm.available // (1024 * 1024)),
            cpu_count=psutil.cpu_count(logical=True) or 1,
            free_disk_gb=round(disk.free / (1024**3), 2),
        )

    def recommend_profile(self, host: HostResources | None = None) -> str:
        """Recommend the richest profile that fits within host RAM."""
        h = host or self.get_host_resources()
        preferred_order = ["full", "balanced", "web-api", "infrastructure", "web", "minimal"]
        available = set(list_profiles(self.project_root))
        for name in preferred_order:
            if name not in available:
                continue
            prof = load_profile(name, self.project_root)
            if h.total_ram_mb >= prof.min_host_ram_mb and h.cpu_count >= prof.recommended_cpus:
                return name
        return "minimal"

    def assess_profile(self, profile_name: str) -> ResourceAssessment:
        """Evaluate whether the host can safely run the requested profile."""
        host = self.get_host_resources()
        profile = load_profile(profile_name, self.project_root)
        recommended = self.recommend_profile(host)
        warnings: list[str] = []

        fits = True
        if host.total_ram_mb < profile.min_host_ram_mb:
            fits = False
            warnings.append(
                f"Host RAM ({host.total_ram_mb} MB) is below minimum for '{profile.name}' "
                f"({profile.min_host_ram_mb} MB). Recommended: '{recommended}'."
            )
        elif host.available_ram_mb < profile.estimated_ram_mb:
            warnings.append(
                f"Available RAM ({host.available_ram_mb} MB) is lower than estimated lab usage "
                f"({profile.estimated_ram_mb} MB)."
            )

        if host.cpu_count < profile.recommended_cpus:
            warnings.append(
                f"Host has {host.cpu_count} vCPU(s); '{profile.name}' recommends "
                f"{profile.recommended_cpus}."
            )

        if host.free_disk_gb < 10.0:
            fits = False
            warnings.append(f"Low free disk space ({host.free_disk_gb} GB); at least 10 GB required.")

        return ResourceAssessment(
            profile=profile,
            host=host,
            fits=fits,
            recommended_profile=recommended,
            warnings=warnings,
        )
