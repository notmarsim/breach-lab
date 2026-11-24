"""CLI tests using Typer CliRunner."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "BreachLab" in result.stdout


def test_cli_validate() -> None:
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "Validation passed" in result.stdout


def test_cli_isolation_check() -> None:
    result = runner.invoke(app, ["isolation-check"])
    assert result.exit_code == 0
    assert "Isolation check PASSED" in result.stdout


def test_cli_scenario_lifecycle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Isolate scenario/snapshot writes to a temp copy of config/profiles
    for sub in ("config", "profiles"):
        src = Path.cwd() / sub
        dst = tmp_path / sub
        dst.mkdir(parents=True)
        for f in src.glob("*.yaml"):
            dst.joinpath(f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "compose.yaml").write_text(
        (Path.cwd() / "compose.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    monkeypatch.setenv("BREACHLAB_ROOT", str(tmp_path))

    res_new = runner.invoke(
        app, ["scenario", "new", "--seed", "845921", "--profile", "minimal", "--mode", "blackbox"]
    )
    assert res_new.exit_code == 0
    assert "845921" in res_new.stdout

    res_info = runner.invoke(app, ["scenario", "info"])
    assert res_info.exit_code == 0
    assert "Black Box mode active" in res_info.stdout

    res_snap = runner.invoke(app, ["snapshot", "create", "--name", "test-snap"])
    assert res_snap.exit_code == 0
    assert "test-snap" in res_snap.stdout

    res_list = runner.invoke(app, ["snapshot", "list"])
    assert res_list.exit_code == 0
    assert "test-snap" in res_list.stdout
