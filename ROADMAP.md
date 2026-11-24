# BreachLab Roadmap

BreachLab is developed incrementally across 9 phases. Each phase produces a runnable and testable state.

## Phase 1 — Foundation (Current)
- Repository structure, documentation, and licensing.
- Idempotent `install.sh` and `uninstall.sh` for Ubuntu Server 24.04 LTS.
- `breachlab` CLI (Typer + Rich).
- Orchestrator modules (Docker, Network, Resource, Scenario, Recovery, Health).
- Declarative resource profiles (`minimal`, `web`, `api`, `web-api`, `infrastructure`, `privesc`, `balanced`, `full`).
- Fail-closed isolation validator and `nftables` firewall template.
- Base `compose.yaml` with management/health foundation and automated unit/isolation/scenario/recovery tests.

## Phase 2 — Corporate Foundation
- Nexora Technologies (`nexora.test`) visual identity & branding.
- Deterministic synthetic data generator (employees, departments, customers, orders, invoices, tickets, emails).
- Core databases (PostgreSQL, MySQL, MongoDB, Redis).
- Corporate Website (`www.nexora.test`), E-commerce (`shop.nexora.test`), Customer Portal (`portal.nexora.test`).

## Phase 3 — Web Applications
- Remaining 7 web apps (`support`, `intranet`, `finance`, `mail`, `files`, `admin`, `legacy`).
- Multi-stack backends (Python, Node.js, PHP, Java, Go).
- Web security educational modules (target: 110) and hardened variants.

## Phase 4 — API Security
- REST (`/api/v1`..`v3`, `beta`, `legacy`), GraphQL, SOAP, WebSocket, Webhooks, OAuth2.
- API security educational modules (target: 50) including secure reference endpoints.

## Phase 5 — Infrastructure
- Linux servers & real services (OpenSSH, vsftpd, Samba, BIND9, Postfix, Dovecot, Net-SNMP, OpenLDAP, RabbitMQ, Squid).
- Infrastructure educational modules (target: 50) + properly hardened services.

## Phase 6 — Linux Privilege Escalation
- Dedicated unprivileged Ubuntu user-space targets (`LINUX01`–`LINUX03`).
- User-space PrivEsc educational modules (target: 40) without container escapes or kernel exploits.

## Phase 7 — Scenario Engine
- Full seed-based variation of IPs, hostnames, users, credentials, active modules, and difficulty tiers.
- Black Box / Gray Box / White Box / Learning / Exam / Hardened mode enforcement.

## Phase 8 — Control Center
- FastAPI backend + React/TypeScript frontend + SQLite persistence.
- Dashboard, Scenario Manager, Discovery Center, Resource Manager, Recovery Center, Personal Notes, Settings.
- Progressive hint system & isolated walkthroughs.

## Phase 9 — Quality Assurance
- Full end-to-end integration tests, resource optimization, security audit, and final goal validation.
