"""Tests for deterministic seed-based Scenario Engine."""

from pathlib import Path

import pytest

from orchestrator.scenario_manager import ScenarioManager


def _prepare_temp_root(tmp_path: Path) -> Path:
    for sub in ("config", "profiles"):
        src = Path.cwd() / sub
        dst = tmp_path / sub
        dst.mkdir(parents=True)
        for f in src.glob("*.yaml"):
            dst.joinpath(f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def test_same_seed_produces_identical_scenario(tmp_path: Path) -> None:
    root = _prepare_temp_root(tmp_path)
    mgr = ScenarioManager(root)

    s1 = mgr.generate(seed=845921, profile="balanced", mode="learning", difficulty="medium")
    s2 = mgr.generate(seed=845921, profile="balanced", mode="learning", difficulty="medium")

    assert s1.scenario_id == s2.scenario_id
    assert s1.synthetic_users == s2.synthetic_users
    assert s1.objectives == s2.objectives


def test_save_and_load_scenario_roundtrip(tmp_path: Path) -> None:
    root = _prepare_temp_root(tmp_path)
    mgr = ScenarioManager(root)

    manifest = mgr.generate(seed=123456, profile="minimal", mode="graybox", difficulty="easy")
    mgr.save(manifest, name="custom-test")
    loaded = mgr.load("custom-test")

    assert loaded.scenario_id == manifest.scenario_id
    assert loaded.seed == 123456
    assert len(mgr.list_scenarios()) == 1


def test_invalid_mode_raises(tmp_path: Path) -> None:
    root = _prepare_temp_root(tmp_path)
    mgr = ScenarioManager(root)
    with pytest.raises(ValueError):
        mgr.generate(seed=111111, mode="invalid-mode")
