"""Unit tests for NetworkManager and ResourceManager."""

import pytest

from orchestrator.config import get_project_root
from orchestrator.network_manager import NetworkManager
from orchestrator.resource_manager import HostResources, ResourceManager


def test_default_topology_has_no_internal_conflicts() -> None:
    nm = NetworkManager(get_project_root())
    conflicts = nm.validate_topology(check_host_routes=False)
    assert conflicts == []


def test_overlapping_subnet_detected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BREACHLAB_NET_DMZ", "10.10.10.0/24")
    nm = NetworkManager(get_project_root())
    conflicts = nm.validate_topology(check_host_routes=False)
    assert any("Overlaps" in c.reason for c in conflicts)


def test_resource_recommendation_for_16gb_host() -> None:
    rm = ResourceManager(get_project_root())
    host_16gb = HostResources(
        total_ram_mb=16384,
        available_ram_mb=12288,
        cpu_count=8,
        free_disk_gb=80.0,
    )
    assert rm.recommend_profile(host_16gb) == "full"


def test_resource_recommendation_for_low_ram_host() -> None:
    rm = ResourceManager(get_project_root())
    host_3gb = HostResources(
        total_ram_mb=3072,
        available_ram_mb=2048,
        cpu_count=2,
        free_disk_gb=25.0,
    )
    assert rm.recommend_profile(host_3gb) == "minimal"


def test_own_breachlab_bridge_routes_are_not_flagged_as_conflicts(monkeypatch: pytest.MonkeyPatch) -> None:
    import ipaddress

    nm = NetworkManager(get_project_root())
    monkeypatch.setattr(nm, "_host_interface_networks", lambda: [("br-bl-ext", ipaddress.IPv4Network("10.10.10.0/24"))])
    monkeypatch.setattr(nm, "_linux_route_networks", lambda: [("br-bl-dmz", ipaddress.IPv4Network("10.10.20.0/24"))])
    conflicts = nm.validate_topology(check_host_routes=True)
    assert conflicts == []
