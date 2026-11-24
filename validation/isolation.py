"""Fail-closed isolation validator for BreachLab compose manifests and runtime."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


FORBIDDEN_HOST_MOUNTS = (
    "/",
    "/etc",
    "/root",
    "/home",
    "/proc",
    "/sys",
    "/var/run/docker.sock",
    "//var/run/docker.sock",
)


@dataclass
class IsolationReport:
    """Result of static and/or runtime isolation checks."""

    passed: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class IsolationValidator:
    """Enforces fail-closed security boundaries for BreachLab."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.compose_file = project_root / "compose.yaml"

    def validate_compose(self, compose_data: dict[str, Any] | None = None) -> IsolationReport:
        """Validate compose.yaml against strict isolation rules."""
        violations: list[str] = []
        warnings: list[str] = []

        if compose_data is None:
            if not self.compose_file.exists():
                return IsolationReport(False, [f"Missing compose file: {self.compose_file}"])
            with self.compose_file.open("r", encoding="utf-8") as handle:
                compose_data = yaml.safe_load(handle) or {}

        services = compose_data.get("services", {})
        if not isinstance(services, dict):
            return IsolationReport(False, ["Invalid 'services' block in compose.yaml."])

        for svc_name, svc in services.items():
            if not isinstance(svc, dict):
                continue

            if svc.get("privileged") is True:
                violations.append(f"Service '{svc_name}' sets privileged: true (forbidden).")

            for ns_key in ("network_mode", "pid", "ipc"):
                if str(svc.get(ns_key, "")).lower() == "host":
                    violations.append(f"Service '{svc_name}' shares host {ns_key} namespace (forbidden).")

            for vol in svc.get("volumes", []) or []:
                vol_str = vol.get("source", "") if isinstance(vol, dict) else str(vol).split(":")[0]
                norm = vol_str.rstrip("/") or "/"
                if "docker.sock" in vol_str:
                    violations.append(f"Service '{svc_name}' mounts Docker socket '{vol_str}' (forbidden).")
                elif norm in FORBIDDEN_HOST_MOUNTS:
                    violations.append(f"Service '{svc_name}' mounts sensitive host path '{vol_str}' (forbidden).")

            for port in svc.get("ports", []) or []:
                port_str = str(port)
                if port_str.startswith("0.0.0.0:"):
                    violations.append(
                        f"Service '{svc_name}' binds port '{port_str}' to 0.0.0.0 (must bind to loopback or lab IP)."
                    )

            deploy_res = svc.get("deploy", {}).get("resources", {}).get("limits", {})
            if not deploy_res.get("memory") and not svc.get("mem_limit"):
                warnings.append(f"Service '{svc_name}' has no explicit memory limit.")

        # Verify internal networks are marked internal: true where expected
        networks = compose_data.get("networks", {})
        for expected_internal in ("database", "restricted", "management"):
            net_cfg = networks.get(expected_internal)
            if isinstance(net_cfg, dict) and net_cfg.get("internal") is not True:
                violations.append(
                    f"Network '{expected_internal}' must set 'internal: true' for segmentation."
                )

        return IsolationReport(passed=len(violations) == 0, violations=violations, warnings=warnings)

    @staticmethod
    def check_linux_nftables() -> tuple[bool, str]:
        """Verify BreachLab nftables table is loaded on Linux hosts."""
        if not sys.platform.startswith("linux"):
            return True, "Non-Linux host detected; nftables check skipped (Docker bridge isolation applies)."
        try:
            proc = subprocess.run(
                ["nft", "list", "table", "inet", "breachlab"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if proc.returncode == 0:
                return True, "nftables table 'inet breachlab' is active."
            return False, "nftables table 'inet breachlab' is not loaded."
        except OSError as exc:
            return False, f"Unable to invoke nft: {exc}"
