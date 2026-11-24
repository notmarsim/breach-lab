"""Network topology validation and CIDR conflict detection."""

from __future__ import annotations

import ipaddress
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import psutil

from orchestrator.config import NetworkDefinition, load_networks


@dataclass
class NetworkConflict:
    """Represents an IP/CIDR overlap or misconfiguration."""

    network_name: str
    subnet: str
    conflict_with: str
    reason: str


class NetworkManager:
    """Validates BreachLab segmented subnets and host route compatibility."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def get_networks(self) -> dict[str, NetworkDefinition]:
        return load_networks(self.project_root)

    @staticmethod
    def _host_interface_networks() -> list[tuple[str, ipaddress.IPv4Network]]:
        """Collect IPv4 networks currently assigned to host interfaces."""
        results: list[tuple[str, ipaddress.IPv4Network]] = []
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if getattr(addr.family, "name", "") == "AF_INET" and addr.address and addr.netmask:
                    try:
                        net = ipaddress.IPv4Network(f"{addr.address}/{addr.netmask}", strict=False)
                        if not net.is_loopback:
                            results.append((iface, net))
                    except ValueError:
                        continue
        return results

    @staticmethod
    def _linux_route_networks() -> list[tuple[str, ipaddress.IPv4Network]]:
        """On Linux, inspect `ip -4 route` for additional non-interface routes."""
        if not sys.platform.startswith("linux"):
            return []
        try:
            proc = subprocess.run(
                ["ip", "-4", "route", "show"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if proc.returncode != 0:
                return []
        except OSError:
            return []

        routes: list[tuple[str, ipaddress.IPv4Network]] = []
        for line in proc.stdout.splitlines():
            parts = line.split()
            if not parts or parts[0] == "default":
                continue
            try:
                net = ipaddress.IPv4Network(parts[0], strict=False)
                routes.append((f"route:{parts[0]}", net))
            except ValueError:
                continue
        return routes

    def validate_topology(self, check_host_routes: bool = True) -> list[NetworkConflict]:
        """Validate CIDR syntax, internal overlaps, and host network conflicts."""
        networks = self.get_networks()
        conflicts: list[NetworkConflict] = []
        parsed: dict[str, ipaddress.IPv4Network] = {}

        for name, net_def in networks.items():
            try:
                net = ipaddress.IPv4Network(net_def.subnet, strict=True)
                parsed[name] = net
            except ValueError as exc:
                conflicts.append(
                    NetworkConflict(name, net_def.subnet, "syntax", f"Invalid IPv4 CIDR: {exc}")
                )
                continue

            try:
                gw = ipaddress.IPv4Address(net_def.gateway)
                if gw not in net:
                    conflicts.append(
                        NetworkConflict(
                            name,
                            net_def.subnet,
                            "gateway",
                            f"Gateway {net_def.gateway} is outside subnet {net_def.subnet}",
                        )
                    )
            except ValueError as exc:
                conflicts.append(
                    NetworkConflict(name, net_def.subnet, "gateway", f"Invalid gateway IP: {exc}")
                )

        # Check pairwise overlaps among BreachLab subnets
        names = list(parsed.keys())
        for i, name_a in enumerate(names):
            for name_b in names[i + 1 :]:
                if parsed[name_a].overlaps(parsed[name_b]):
                    conflicts.append(
                        NetworkConflict(
                            name_a,
                            str(parsed[name_a]),
                            name_b,
                            f"Overlaps with BreachLab network '{name_b}' ({parsed[name_b]})",
                        )
                    )

        if check_host_routes:
            host_nets = self._host_interface_networks() + self._linux_route_networks()
            for name, net in parsed.items():
                bridge_name = networks[name].bridge
                for iface, host_net in host_nets:
                    if iface == bridge_name:
                        continue
                    if net.overlaps(host_net):
                        conflicts.append(
                            NetworkConflict(
                                name,
                                str(net),
                                iface,
                                f"Overlaps with existing host network {host_net} on {iface}",
                            )
                        )
        return conflicts
