# BreachLab Architecture

## 1. Design Principles

1. **Realistic Enterprise Simulation**: Models a cohesive fictional company (**Nexora Technologies**, `nexora.test`) rather than isolated vulnerable pages.
2. **No Nested Virtualization**: Uses Linux containers via Docker and Docker Compose, allowing execution inside standard VMs (VirtualBox, VMware, Hyper-V, Proxmox) or bare-metal Ubuntu Server 24.04 LTS.
3. **Fail-Closed Isolation**: Target networks are strictly isolated from the internet, home/corporate LANs, and the host management plane. If isolation checks fail, vulnerable environments must not start.
4. **Control Plane Separation**: The Control Center (`10.10.60.0/24` / loopback) is out-of-scope for pentesting and has no direct Docker daemon exposure to the frontend.
5. **Declarative & Modular**: Profiles, network topology, challenge modules, and scenarios are defined in YAML and orchestrated in Python.

## 2. Technology Stack

| Component | Technology |
|---|---|
| Host OS | Ubuntu Server 24.04 LTS |
| Custom Target Containers | Ubuntu 24.04 LTS (Ubuntu 22.04 LTS for legacy) |
| Provisioning & Orchestration | Docker + Docker Compose |
| Installer | Idempotent Bash (`install.sh`, `uninstall.sh`) |
| CLI | Python 3.11+ + Typer + Rich |
| Orchestrator & Scenario Engine | Python + Pydantic + PyYAML |
| Firewall / Segmentation | `nftables` + Docker dedicated bridge networks |
| Control Center (Planned - Phase 8) | FastAPI (Backend), React + TypeScript (Frontend), SQLite |
| Reverse Proxy | Nginx |
| Persistence | Docker Volumes + Host Snapshot Directory |
| Automated Testing | Pytest |

## 3. Network Topology

All subnets are configurable via `.env` and `config/networks.yaml` to prevent local IP collisions:

| Network | Default Subnet | Internal | Purpose |
|---|---|---|---|
| `external` | `10.10.10.0/24` | No (Host/VM Lab Interface) | Pentester machine (e.g., Kali Linux) |
| `dmz` | `10.10.20.0/24` | Yes (Controlled ingress from `external`) | Public-facing web & API entrypoints |
| `internal` | `10.10.30.0/24` | Yes | Intranet, Helpdesk, Webmail, File Manager, Legacy |
| `database` | `10.10.40.0/24` | Yes (`internal: true`) | PostgreSQL, MySQL, MongoDB, Redis |
| `restricted` | `10.10.50.0/24` | Yes (`internal: true`) | Admin Panel, Backups, Linux PrivEsc targets |
| `management` | `10.10.60.0/24` | Host-only / Loopback | Control Center & Lab Telemetry |

## 4. Core Subsystems

### 4.1. CLI (`cli/`)
Provides the `breachlab` command-line interface for lifecycle (`install`, `doctor`, `start`, `stop`, `restart`, `status`, `logs`, `update`, `cleanup`, `uninstall`), scenarios (`scenario new|list|save|load|info`), recovery (`reset`, `snapshot create|list|restore`), and security (`validate`, `isolation-check`).

### 4.2. Orchestrator (`orchestrator/`)
- `docker_manager.py`: Wraps Docker & Docker Compose execution with safe subprocess handling.
- `network_manager.py`: Validates subnet configurations, detects host routing/CIDR conflicts, and manages network segmentation.
- `resource_manager.py`: Detects host RAM/CPU via `psutil`, recommends appropriate profiles, and enforces container memory/CPU limits.
- `scenario_manager.py`: Generates, saves, loads, and inspects deterministic seed-based scenario manifests.
- `recovery_manager.py`: Handles per-target resets, global resets (with progress preservation), and consistent snapshots.
- `health_manager.py`: Performs container health diagnostics and service readiness checks.

### 4.3. Validation & Isolation (`validation/`)
- `isolation.py`: Static and runtime fail-closed verification of `compose.yaml` and active containers:
  - Rejects `privileged: true`.
  - Rejects `/var/run/docker.sock` mounts.
  - Rejects sensitive host directory mounts (`/`, `/etc`, `/root`, `/home`, `/proc`, `/sys`).
  - Rejects `network_mode: host`, `pid: host`, `ipc: host`.
  - Verifies target networks do not bind vulnerable services to `0.0.0.0` on non-lab interfaces.
  - Verifies `nftables` egress/LAN-blocking rules on Linux hosts.

### 4.4. Out-of-Scope Boundaries
Per project scope, BreachLab does **not** implement Active Directory, Windows targets, Cloud Pentesting, Container Escape, Kubernetes, Binary/Kernel Exploitation, nested virtualization (QEMU/KVM/Libvirt), competitive rankings, or mandatory finding reports.
