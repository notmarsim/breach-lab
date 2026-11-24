"""Deterministic, seed-based Scenario Engine for reproducible lab configurations."""

from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from orchestrator.config import load_config, load_networks, load_profile


class ScenarioManifest(BaseModel):
    """Reproducible scenario definition generated from a seed."""

    scenario_id: str
    seed: int
    catalog_version: str
    profile: str
    mode: str
    difficulty: str
    created_at: str
    domain: str = "nexora.test"
    networks: dict[str, str] = Field(default_factory=dict)
    services: list[str] = Field(default_factory=list)
    synthetic_users: list[dict[str, str]] = Field(default_factory=list)
    objectives: list[dict[str, str]] = Field(default_factory=list)


class ScenarioManager:
    """Creates, saves, loads, and lists reproducible BreachLab scenarios."""

    VALID_MODES = ("learning", "blackbox", "graybox", "whitebox", "independent", "enterprise", "exam", "hardened")
    VALID_DIFFICULTIES = ("easy", "medium", "hard", "insane")

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.scenarios_dir = project_root / "scenarios"
        self.state_dir = project_root / ".breachlab"
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _deterministic_id(seed: int, catalog_version: str, profile: str, mode: str, difficulty: str) -> str:
        payload = f"{seed}:{catalog_version}:{profile}:{mode}:{difficulty}".encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()[:10]
        return f"scn-{seed}-{digest}"

    def generate(
        self,
        seed: int | None = None,
        profile: str = "balanced",
        mode: str = "learning",
        difficulty: str = "medium",
    ) -> ScenarioManifest:
        """Generate a deterministic scenario manifest from seed and configuration."""
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Valid: {', '.join(self.VALID_MODES)}")
        if difficulty not in self.VALID_DIFFICULTIES:
            raise ValueError(
                f"Invalid difficulty '{difficulty}'. Valid: {', '.join(self.VALID_DIFFICULTIES)}"
            )

        cfg = load_config(self.project_root)
        prof = load_profile(profile, self.project_root)
        nets = load_networks(self.project_root)

        actual_seed = seed if seed is not None else random.SystemRandom().randint(100000, 999999)
        rng = random.Random(actual_seed)

        first_names = ["alice", "bruno", "carla", "diego", "elena", "felipe", "gabriela", "hugo"]
        last_names = ["silva", "santos", "oliveira", "costa", "ferreira", "almeida", "rocha", "lima"]
        departments = ["IT", "Engineering", "HR", "Finance", "Support", "Sales", "Operations"]

        users: list[dict[str, str]] = []
        chosen_firsts = rng.sample(first_names, 4)
        for idx, fname in enumerate(chosen_firsts):
            lname = rng.choice(last_names)
            dept = departments[idx % len(departments)]
            users.append(
                {
                    "username": f"{fname}.{lname}",
                    "email": f"{fname}.{lname}@nexora.test",
                    "department": dept,
                    "role": "employee",
                }
            )

        scenario_id = self._deterministic_id(actual_seed, cfg.version, profile, mode, difficulty)
        flag_hash = hashlib.sha256(f"flag:{scenario_id}".encode("utf-8")).hexdigest()[:12]

        objectives = [
            {
                "id": "obj-foundation-health",
                "title": "Verify Nexora lab perimeter availability",
                "category": "reconnaissance",
                "difficulty": "easy",
                "flag_token": f"BL{{{flag_hash}}}",
            }
        ]

        return ScenarioManifest(
            scenario_id=scenario_id,
            seed=actual_seed,
            catalog_version=cfg.version,
            profile=profile,
            mode=mode,
            difficulty=difficulty,
            created_at=datetime.now(timezone.utc).isoformat(),
            domain=cfg.organization.get("domain", "nexora.test"),
            networks={name: net.subnet for name, net in nets.items()},
            services=list(prof.services),
            synthetic_users=users,
            objectives=objectives,
        )

    def save(self, manifest: ScenarioManifest, name: str | None = None) -> Path:
        """Persist a scenario manifest as YAML under scenarios/."""
        filename = f"{name or manifest.scenario_id}.yaml"
        target = self.scenarios_dir / filename
        with target.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(manifest.model_dump(), handle, sort_keys=False)
        self.set_active(manifest)
        return target

    def load(self, name_or_id: str) -> ScenarioManifest:
        """Load a saved scenario manifest by name or ID."""
        candidate = self.scenarios_dir / f"{name_or_id.removesuffix('.yaml')}.yaml"
        if not candidate.exists():
            raise FileNotFoundError(f"Scenario '{name_or_id}' not found in {self.scenarios_dir}")
        with candidate.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        manifest = ScenarioManifest(**data)
        self.set_active(manifest)
        return manifest

    def list_scenarios(self) -> list[ScenarioManifest]:
        """List all saved scenario manifests."""
        results: list[ScenarioManifest] = []
        for path in sorted(self.scenarios_dir.glob("*.yaml")):
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
            results.append(ScenarioManifest(**data))
        return results

    def set_active(self, manifest: ScenarioManifest) -> None:
        active_file = self.state_dir / "active_scenario.json"
        active_file.write_text(json.dumps(manifest.model_dump(), indent=2), encoding="utf-8")

    def get_active(self) -> ScenarioManifest | None:
        active_file = self.state_dir / "active_scenario.json"
        if not active_file.exists():
            return None
        data = json.loads(active_file.read_text(encoding="utf-8"))
        return ScenarioManifest(**data)
