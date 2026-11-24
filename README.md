# BreachLab — Enterprise Pentesting Training Environment

BreachLab is a local, isolated, self-provisioned **Enterprise Cyber Range** simulating **Nexora Technologies** (`nexora.test`), a fictional enterprise with interconnected web applications, APIs, Linux servers, databases, network services, employees, customers, and corporate data.

> **Disclaimer**: BreachLab is designed exclusively for **local, authorized, and isolated** offensive security training and defensive remediation validation. Never expose BreachLab networks or containers to the internet or production networks.

## Quick Start (Ubuntu Server 24.04 LTS)

```bash
git clone git@github.com:notmarsim/breach-lab.git
cd breach-lab
sudo ./install.sh
breachlab start --profile balanced
```

## Key Features (Planned & Incremental)

- **Zero Nested Virtualization**: Runs natively on Docker & Docker Compose inside any Ubuntu Server 24.04 LTS host or VM (VirtualBox, VMware, Hyper-V, Proxmox, bare metal).
- **Segmented Corporate Topology**: 6 configurable subnets (`External`, `DMZ`, `Internal`, `Database`, `Restricted`, `Management`) with fail-closed `nftables` isolation.
- **Resource Profiles**: `minimal`, `web`, `api`, `web-api`, `infrastructure`, `privesc`, `balanced`, `full`.
- **Reproducible Scenario Engine**: Deterministic seed-based scenario generation (`breachlab scenario new --seed 845921`).
- **Control Center**: Dedicated management plane (FastAPI + React/TypeScript) strictly separated from the pentest attack surface.

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Roadmap](ROADMAP.md)
- [Implementation Status](IMPLEMENTATION_STATUS.md)
- [Security & Isolation](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
