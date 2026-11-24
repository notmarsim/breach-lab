"""Enhanced deterministic Scenario Engine combining catalog, synthetic data, and modes."""

from __future__ import annotations

import hashlib
import random
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from orchestrator.config import load_config, load_networks, load_profile
from synthetic_data.generator import generate_enterprise_dataset
from vulnerability_catalog.loader import EducationalModule, load_catalog


DIFFICULTY_ORDER = {"easy": 1, "medium": 2, "hard": 3, "insane": 4}


class CompiledScenario(BaseModel):
    """Full compiled scenario including corporate dataset and selected modules."""

    scenario_id: str
    seed: int
    catalog_version: str
    profile: str
    mode: str
    difficulty: str
    domain: str
    networks: dict[str, str]
    services: list[str]
    modules: list[dict[str, Any]] = Field(default_factory=list)
    flags: dict[str, str] = Field(default_factory=dict)
    dataset_summary: dict[str, int] = Field(default_factory=dict)


class ScenarioEngine:
    """Compiles deterministic, reproducible training scenarios from a seed."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def compile(
        self,
        seed: int,
        profile: str = "balanced",
        mode: str = "learning",
        difficulty: str = "medium",
    ) -> CompiledScenario:
        if difficulty not in DIFFICULTY_ORDER:
            raise ValueError(f"Unsupported difficulty '{difficulty}'.")

        cfg = load_config(self.project_root)
        prof = load_profile(profile, self.project_root)
        nets = load_networks(self.project_root)
        catalog = load_catalog(self.project_root)
        dataset = generate_enterprise_dataset(seed=seed)

        max_rank = DIFFICULTY_ORDER[difficulty]
        eligible: list[EducationalModule] = [
            m for m in catalog if DIFFICULTY_ORDER.get(m.difficulty, 2) <= max_rank
        ]

        rng = random.Random(seed)
        selected = sorted(eligible, key=lambda m: (rng.random(), m.id))

        scenario_id = f"scn-{seed}-{hashlib.sha256(f'{seed}:{profile}:{mode}:{difficulty}'.encode()).hexdigest()[:10]}"
        flags: dict[str, str] = {}
        module_entries: list[dict[str, Any]] = []
        for mod in selected:
            token = hashlib.sha256(f"{scenario_id}:{mod.id}".encode("utf-8")).hexdigest()[:12]
            flags[mod.id] = f"BL{{{token}}}"
            module_entries.append(
                {
                    "id": mod.id,
                    "name": mod.name,
                    "domain": mod.domain,
                    "category": mod.category,
                    "difficulty": mod.difficulty,
                    "target_service": mod.target_service,
                    "validation_method": mod.validation_method,
                    "hardened": mode == "hardened",
                }
            )

        return CompiledScenario(
            scenario_id=scenario_id,
            seed=seed,
            catalog_version=cfg.version,
            profile=profile,
            mode=mode,
            difficulty=difficulty,
            domain=cfg.organization.get("domain", "nexora.test"),
            networks={k: v.subnet for k, v in nets.items()},
            services=list(prof.services),
            modules=module_entries,
            flags=flags,
            dataset_summary={
                "employees": len(dataset["employees"]),
                "customers": len(dataset["customers"]),
                "orders": len(dataset["orders"]),
                "invoices": len(dataset["invoices"]),
                "tickets": len(dataset["tickets"]),
            },
        )

    @staticmethod
    def public_view(scenario: CompiledScenario) -> dict[str, Any]:
        """Return spoiler-safe view of a scenario (enforces Black Box & Exam rules)."""
        base = {
            "scenario_id": scenario.scenario_id,
            "profile": scenario.profile,
            "mode": scenario.mode,
            "difficulty": scenario.difficulty,
            "domain": scenario.domain,
        }
        if scenario.mode == "blackbox":
            base["authorized_scope"] = {"domain": scenario.domain, "external_subnet": scenario.networks.get("external")}
            return base
        base["services"] = scenario.services
        base["module_count"] = len(scenario.modules)
        return base
