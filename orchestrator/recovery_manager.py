"""Recovery, target reset, and snapshot management."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from orchestrator.docker_manager import DockerManager


@dataclass
class SnapshotInfo:
    """Metadata describing a saved lab snapshot."""

    name: str
    created_at: str
    includes_progress: bool
    path: Path


class RecoveryManager:
    """Manages target resets, global resets, and consistent snapshots."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.state_dir = project_root / ".breachlab"
        self.snapshots_dir = project_root / "snapshots"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.docker = DockerManager(project_root)

    def reset_target(self, target: str) -> tuple[bool, str]:
        """Recreate a single service container without clearing user progress."""
        if not self.docker.is_docker_installed() or not self.docker.daemon_ready():
            return False, "Docker daemon is not available."
        res = self.docker.compose(["up", "-d", "--force-recreate", target])
        if not res.ok:
            return False, res.stderr or f"Failed to reset target '{target}'."
        return True, f"Target '{target}' reset successfully (user progress preserved)."

    def reset_global(self, preserve_progress: bool = True) -> tuple[bool, str]:
        """Reset all lab containers and optionally clear user progress."""
        if self.docker.is_docker_installed() and self.docker.daemon_ready():
            res = self.docker.down(remove_volumes=True)
            if not res.ok:
                return False, res.stderr or "Failed to tear down containers."

        if not preserve_progress:
            progress_file = self.state_dir / "progress.json"
            if progress_file.exists():
                progress_file.unlink()
        return True, (
            "Global reset completed (progress preserved)."
            if preserve_progress
            else "Global reset completed (progress cleared)."
        )

    def create_snapshot(self, name: str | None = None, include_progress: bool = True) -> SnapshotInfo:
        """Create a consistent snapshot of lab state and active scenario."""
        snap_name = name or f"snap-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        snap_dir = self.snapshots_dir / snap_name
        if snap_dir.exists():
            raise FileExistsError(f"Snapshot '{snap_name}' already exists.")
        snap_dir.mkdir(parents=True, exist_ok=True)

        state_copy = snap_dir / "state"
        if self.state_dir.exists():
            shutil.copytree(
                self.state_dir,
                state_copy,
                ignore=shutil.ignore_patterns() if include_progress else shutil.ignore_patterns("progress.json"),
            )
        else:
            state_copy.mkdir(parents=True, exist_ok=True)

        meta = {
            "name": snap_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "includes_progress": include_progress,
        }
        (snap_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return SnapshotInfo(
            name=snap_name,
            created_at=meta["created_at"],
            includes_progress=include_progress,
            path=snap_dir,
        )

    def list_snapshots(self) -> list[SnapshotInfo]:
        """List available snapshots sorted newest first."""
        snaps: list[SnapshotInfo] = []
        for entry in sorted(self.snapshots_dir.iterdir(), reverse=True):
            meta_file = entry / "metadata.json"
            if not entry.is_dir() or not meta_file.exists():
                continue
            data = json.loads(meta_file.read_text(encoding="utf-8"))
            snaps.append(
                SnapshotInfo(
                    name=data["name"],
                    created_at=data["created_at"],
                    includes_progress=bool(data.get("includes_progress", True)),
                    path=entry,
                )
            )
        return snaps

    def restore_snapshot(self, name: str) -> SnapshotInfo:
        """Restore lab state from a named snapshot."""
        snap_dir = self.snapshots_dir / name
        meta_file = snap_dir / "metadata.json"
        if not meta_file.exists():
            raise FileNotFoundError(f"Snapshot '{name}' not found.")

        state_src = snap_dir / "state"
        if state_src.exists():
            if self.state_dir.exists():
                shutil.rmtree(self.state_dir)
            shutil.copytree(state_src, self.state_dir)

        data = json.loads(meta_file.read_text(encoding="utf-8"))
        return SnapshotInfo(
            name=data["name"],
            created_at=data["created_at"],
            includes_progress=bool(data.get("includes_progress", True)),
            path=snap_dir,
        )
