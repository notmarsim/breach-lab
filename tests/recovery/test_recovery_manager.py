"""Tests for RecoveryManager snapshots and progress preservation."""

from pathlib import Path

from orchestrator.recovery_manager import RecoveryManager


def test_snapshot_create_list_restore(tmp_path: Path) -> None:
    mgr = RecoveryManager(tmp_path)
    progress = tmp_path / ".breachlab" / "progress.json"
    progress.write_text('{"completed": ["obj-1"]}', encoding="utf-8")

    snap = mgr.create_snapshot(name="baseline")
    assert snap.name == "baseline"
    assert len(mgr.list_snapshots()) == 1

    progress.write_text('{"completed": []}', encoding="utf-8")
    mgr.restore_snapshot("baseline")
    assert '"obj-1"' in progress.read_text(encoding="utf-8")


def test_global_reset_preserves_or_clears_progress(tmp_path: Path, monkeypatch) -> None:
    mgr = RecoveryManager(tmp_path)
    monkeypatch.setattr(mgr.docker, "is_docker_installed", lambda: False)

    progress = tmp_path / ".breachlab" / "progress.json"
    progress.write_text('{"completed": ["obj-1"]}', encoding="utf-8")

    ok, _ = mgr.reset_global(preserve_progress=True)
    assert ok is True
    assert progress.exists()

    ok, _ = mgr.reset_global(preserve_progress=False)
    assert ok is True
    assert not progress.exists()
