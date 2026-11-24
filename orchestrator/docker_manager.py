"""Safe Docker and Docker Compose orchestration wrapper."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CommandResult:
    """Structured result from executing a system command."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class DockerManager:
    """Manages Docker Compose lifecycle and container inspection."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.compose_file = project_root / "compose.yaml"

    @staticmethod
    def is_docker_installed() -> bool:
        return shutil.which("docker") is not None

    def run(self, args: list[str], timeout: int = 120) -> CommandResult:
        """Execute a docker CLI command without invoking a shell."""
        if not self.is_docker_installed():
            return CommandResult(127, "", "Docker binary not found in PATH.")
        proc = subprocess.run(
            ["docker", *args],
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return CommandResult(proc.returncode, proc.stdout.strip(), proc.stderr.strip())

    def compose(
        self,
        args: list[str],
        profiles: list[str] | None = None,
        timeout: int = 180,
    ) -> CommandResult:
        """Execute a docker compose command with optional profile flags."""
        cmd = ["compose", "-f", str(self.compose_file)]
        for prof in profiles or []:
            cmd.extend(["--profile", prof])
        cmd.extend(args)
        return self.run(cmd, timeout=timeout)

    def daemon_ready(self) -> bool:
        """Return True if the Docker daemon responds to `docker info`."""
        res = self.run(["info", "--format", "{{.ServerVersion}}"], timeout=10)
        return res.ok and bool(res.stdout)

    def up(self, profiles: list[str] | None = None, build: bool = False) -> CommandResult:
        """Start the lab environment in detached mode."""
        args = ["up", "-d", "--remove-orphans"]
        if build:
            args.append("--build")
        return self.compose(args, profiles=profiles)

    def down(self, profiles: list[str] | None = None, remove_volumes: bool = False) -> CommandResult:
        """Stop and remove lab containers."""
        args = ["down", "--remove-orphans"]
        if remove_volumes:
            args.append("-v")
        return self.compose(args, profiles=profiles)

    def ps(self, profiles: list[str] | None = None) -> list[dict]:
        """Return parsed container status entries for the project."""
        res = self.compose(["ps", "--format", "json"], profiles=profiles, timeout=30)
        if not res.ok or not res.stdout:
            return []
        entries: list[dict] = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return entries

    def logs(self, service: str | None = None, tail: int = 100) -> CommandResult:
        """Fetch recent container logs."""
        args = ["logs", "--tail", str(tail)]
        if service:
            args.append(service)
        return self.compose(args, timeout=30)
