#!/usr/bin/env bash
set -euo pipefail

apt update
apt install -y git curl ufw ca-certificates gnupg lsb-release

ufw allow OpenSSH
ufw --force enable

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

systemctl enable --now docker

echo "VPS base ready. Copy project to /opt/agency-operator, then run:"
echo "cp .env.example .env && docker compose up -d --build"
