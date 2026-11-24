#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_SYMLINK="/usr/local/bin/breachlab"
NFT_DEST="/etc/nftables.d/breachlab.nft"

if [[ "${EUID}" -ne 0 ]]; then
  echo "[ERROR] Please run uninstall.sh with sudo." >&2
  exit 1
fi

echo "[INFO] Stopping BreachLab containers and removing lab networks..."
if command -v docker >/dev/null 2>&1 && [[ -f "${SCRIPT_DIR}/compose.yaml" ]]; then
  docker compose -f "${SCRIPT_DIR}/compose.yaml" --profile core down --remove-orphans || true
fi

if command -v nft >/dev/null 2>&1; then
  nft delete table inet breachlab 2>/dev/null || true
fi
rm -f "${NFT_DEST}"
rm -f "${CLI_SYMLINK}"
rm -rf "${SCRIPT_DIR}/.venv"

echo "[INFO] BreachLab uninstalled. Repository files and snapshots in ${SCRIPT_DIR} were preserved."
