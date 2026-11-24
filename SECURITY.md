# Security & Isolation Policy

## 1. Authorized Training Scope Only
BreachLab contains intentionally vulnerable applications, services, and configurations for **local, authorized, isolated offensive security training**.
- Do **not** deploy BreachLab on public cloud instances with public IPs or internet-facing interfaces.
- Do **not** bridge the BreachLab VM to a production or home LAN during active training.
- Use a dedicated, disposable Ubuntu Server 24.04 LTS VM connected to an **isolated virtual network** (e.g., Host-Only or Internal Network in VirtualBox/VMware/Proxmox) shared only with your Kali Linux training VM.

## 2. Fail-Closed Isolation Architecture
BreachLab enforces a **fail-closed** policy: if isolation checks fail, vulnerable lab containers must not start.

### Mandatory Controls
1. **Dedicated Docker Networks**: Segmented subnets (`external`, `dmz`, `internal`, `database`, `restricted`, `management`). Internal tiers (`database`, `restricted`) are marked `internal: true` in Docker Compose.
2. **Host Firewall (`nftables`)**: Target bridge interfaces (`br-bl-*`) are blocked from initiating outbound connections to the internet or RFC1918 host/LAN networks, while permitting return traffic for authorized lab sessions.
3. **No Privileged Containers**: `privileged: true` is strictly prohibited across all service definitions.
4. **No Docker Socket Mounting**: `/var/run/docker.sock` must never be mounted into any target container.
5. **No Sensitive Host Mounts or Namespace Sharing**: Host `/`, `/etc`, `/root`, `/home`, `/proc`, `/sys`, and `network_mode: host`, `pid: host`, `ipc: host` are prohibited for targets.
6. **Control Center Separation**: The Control Center runs on the `management` plane (`127.0.0.1` / `10.10.60.0/24`) and never exposes raw Docker daemon access to the frontend.
7. **Synthetic Data Only**: All identities, emails (`nexora.test`), credentials, payment flows, and logs are 100% synthetic. No external emails or real payments are permitted.

## 3. Verifying Isolation
Run `breachlab isolation-check` or `breachlab doctor` before starting any training session.
