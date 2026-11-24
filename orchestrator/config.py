"""Configuration loader and Pydantic schemas for BreachLab."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


def get_project_root(start_path: Path | None = None) -> Path:
    """Resolve the BreachLab repository root directory."""
    env_root = os.environ.get("BREACHLAB_ROOT")
    if env_root:
        candidate = Path(env_root).resolve()
        if (candidate / "compose.yaml").exists() or (candidate / "config" / "breachlab.yaml").exists():
            return candidate

    current = (start_path or Path(__file__)).resolve()
    for parent in [current, *current.parents]:
        if (parent / "config" / "breachlab.yaml").exists():
            return parent
    return Path.cwd().resolve()


class NetworkDefinition(BaseModel):
    """Schema for a segmented BreachLab network."""

    subnet: str
    gateway: str
    bridge: str
    internal: bool = True
    purpose: str = ""


class ProfileLimits(BaseModel):
    """Default container resource limits for a profile."""

    default_memory: str = "256m"
    default_cpus: str = "0.5"


class ResourceProfile(BaseModel):
    """Schema for a BreachLab resource profile."""

    name: str
    description: str
    estimated_ram_mb: int
    min_host_ram_mb: int
    recommended_cpus: int
    compose_profiles: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    limits: ProfileLimits = Field(default_factory=ProfileLimits)


class BreachLabConfig(BaseModel):
    """Top-level declarative configuration."""

    version: str = "0.1.0"
    organization: dict[str, str] = Field(default_factory=dict)
    defaults: dict[str, Any] = Field(default_factory=dict)
    paths: dict[str, str] = Field(default_factory=dict)


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file safely as a dictionary."""
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def load_config(root: Path | None = None) -> BreachLabConfig:
    """Load the main BreachLab configuration."""
    project_root = root or get_project_root()
    data = load_yaml(project_root / "config" / "breachlab.yaml")
    return BreachLabConfig(**data)


def load_networks(root: Path | None = None) -> dict[str, NetworkDefinition]:
    """Load network topology definitions with optional environment overrides."""
    project_root = root or get_project_root()
    raw = load_yaml(project_root / "config" / "networks.yaml")
    nets_raw = raw.get("networks", {})
    result: dict[str, NetworkDefinition] = {}
    for name, cfg in nets_raw.items():
        env_key = f"BREACHLAB_NET_{name.upper()}"
        net_data = dict(cfg)
        if env_key in os.environ and os.environ[env_key].strip():
            net_data["subnet"] = os.environ[env_key].strip()
        result[name] = NetworkDefinition(**net_data)
    return result


def load_profile(name: str, root: Path | None = None) -> ResourceProfile:
    """Load a named resource profile from profiles/<name>.yaml."""
    project_root = root or get_project_root()
    profile_path = project_root / "profiles" / f"{name}.yaml"
    if not profile_path.exists():
        available = list_profiles(project_root)
        raise FileNotFoundError(
            f"Profile '{name}' not found. Available profiles: {', '.join(available)}"
        )
    data = load_yaml(profile_path)
    return ResourceProfile(**data)


def list_profiles(root: Path | None = None) -> list[str]:
    """Return all available profile names sorted alphabetically."""
    project_root = root or get_project_root()
    profiles_dir = project_root / "profiles"
    if not profiles_dir.exists():
        return []
    return sorted(p.stem for p in profiles_dir.glob("*.yaml"))
