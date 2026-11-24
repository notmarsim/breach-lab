"""Unit tests for BreachLab declarative configuration and resource profiles."""

from pathlib import Path

import pytest

from orchestrator.config import (
    get_project_root,
    list_profiles,
    load_config,
    load_networks,
    load_profile,
)

EXPECTED_PROFILES = [
    "api",
    "balanced",
    "full",
    "infrastructure",
    "minimal",
    "privesc",
    "web",
    "web-api",
]


def test_load_main_config() -> None:
    root = get_project_root()
    cfg = load_config(root)
    assert cfg.version == "0.1.0"
    assert cfg.organization["domain"] == "nexora.test"
    assert cfg.defaults["strict_isolation"] is True


def test_all_eight_profiles_exist_and_parse() -> None:
    root = get_project_root()
    profiles = list_profiles(root)
    assert profiles == EXPECTED_PROFILES
    for name in profiles:
        prof = load_profile(name, root)
        assert prof.name == name
        assert prof.estimated_ram_mb > 0
        assert "core" in prof.compose_profiles


def test_missing_profile_raises() -> None:
    root = get_project_root()
    with pytest.raises(FileNotFoundError):
        load_profile("nonexistent-profile", root)


def test_network_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    root: Path = get_project_root()
    monkeypatch.setenv("BREACHLAB_NET_DMZ", "10.99.20.0/24")
    nets = load_networks(root)
    assert nets["dmz"].subnet == "10.99.20.0/24"
    assert set(nets.keys()) == {"external", "dmz", "internal", "database", "restricted", "management"}
