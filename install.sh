#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
CLI_SYMLINK="/usr/local/bin/breachlab"
NFT_DEST="/etc/nftables.d/breachlab.nft"

log_info()  { echo "[INFO]  $*"; }
log_warn()  { echo "[WARN]  $*"; }
log_error() { echo "[ERROR] $*" >&2; }

if [[ "${EUID}" -ne 0 ]]; then
  log_error "Please run install.sh with sudo: sudo ./install.sh"
  exit 1
fi

# 1. Verify Linux distribution
if [[ ! -f /etc/os-release ]]; then
  log_error "Cannot detect Linux distribution (/etc/os-release missing)."
  exit 1
fi
# shellcheck disable=SC1091
source /etc/os-release
if [[ "${ID:-}" != "ubuntu" || "${VERSION_ID:-}" != "24.04" ]]; then
  log_warn "Detected ${PRETTY_NAME:-unknown}. BreachLab targets Ubuntu Server 24.04 LTS."
fi

# 2. Verify architecture
ARCH="$(uname -m)"
if [[ "${ARCH}" != "x86_64" && "${ARCH}" != "aarch64" ]]; then
  log_error "Unsupported CPU architecture: ${ARCH}. Expected x86_64 or aarch64."
  exit 1
fi
log_info "Architecture verified: ${ARCH}"

# 3. Verify RAM and storage
TOTAL_RAM_MB="$(awk '/MemTotal/ {printf "%d", $2/1024}' /proc/meminfo)"
FREE_DISK_GB="$(df -BG --output=avail "${SCRIPT_DIR}" | tail -n 1 | tr -dc '0-9')"
if [[ "${TOTAL_RAM_MB}" -lt 2048 ]]; then
  log_error "At least 2048 MB RAM required (detected ${TOTAL_RAM_MB} MB)."
  exit 1
fi
if [[ "${FREE_DISK_GB}" -lt 10 ]]; then
  log_error "At least 10 GB free disk space required (detected ${FREE_DISK_GB} GB)."
  exit 1
fi
log_info "Resources verified: ${TOTAL_RAM_MB} MB RAM, ${FREE_DISK_GB} GB free disk."

# 4. Install system dependencies
log_info "Installing base system dependencies..."
apt-get update -qq
apt-get install -y -qq ca-certificates curl gnupg lsb-release python3 python3-venv python3-pip nftables iproute2

# 5. Install Docker & Docker Compose plugin (idempotent)
if ! command -v docker >/dev/null 2>&1; then
  log_info "Installing Docker Engine and Compose plugin..."
  install -m 0755 -d /etc/apt/keyrings
  if [[ ! -f /etc/apt/keyrings/docker.asc ]]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
  fi
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "${VERSION_CODENAME}") stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update -qq
  apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable --now docker
else
  log_info "Docker already installed: $(docker --version)"
fi

if [[ -n "${SUDO_USER:-}" ]]; then
  usermod -aG docker "${SUDO_USER}" || true
fi

# 6. Create required directories
mkdir -p "${SCRIPT_DIR}/.breachlab" "${SCRIPT_DIR}/scenarios" "${SCRIPT_DIR}/snapshots" "${SCRIPT_DIR}/logs"

# 7. Initialize .env idempotently
if [[ ! -f "${SCRIPT_DIR}/.env" && -f "${SCRIPT_DIR}/.env.example" ]]; then
  cp "${SCRIPT_DIR}/.env.example" "${SCRIPT_DIR}/.env"
  log_info "Initialized .env from .env.example."
fi

# 8. Install BreachLab Python package & CLI in isolated venv
log_info "Setting up Python virtual environment and breachlab CLI..."
if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi
"${VENV_DIR}/bin/pip" install --quiet --upgrade pip
"${VENV_DIR}/bin/pip" install --quiet -e "${SCRIPT_DIR}[dev]"

cat > "${CLI_SYMLINK}" <<EOF
#!/usr/bin/env bash
export BREACHLAB_ROOT="${SCRIPT_DIR}"
exec "${VENV_DIR}/bin/breachlab" "\$@"
EOF
chmod 0755 "${CLI_SYMLINK}"

# 9. Pull/build base images
log_info "Building BreachLab base Ubuntu image..."
docker build -t breachlab/ubuntu-base:24.04 "${SCRIPT_DIR}/images/ubuntu-base"
docker compose -f "${SCRIPT_DIR}/compose.yaml" --profile core pull

# 10. Configure nftables fail-closed isolation (without disabling host firewall)
log_info "Applying nftables fail-closed lab isolation rules..."
mkdir -p /etc/nftables.d
cp "${SCRIPT_DIR}/infrastructure/firewall/nftables.conf.template" "${NFT_DEST}"
nft -f "${NFT_DEST}"

# 11. Run validation and unit/isolation tests
log_info "Running BreachLab validation and automated tests..."
"${CLI_SYMLINK}" validate
"${VENV_DIR}/bin/pytest" "${SCRIPT_DIR}/tests"

log_info "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Ensure your VM uses an isolated virtual network (no bridge to physical LAN)."
echo "  2. Run: breachlab doctor"
echo "  3. Run: breachlab start --profile balanced"
