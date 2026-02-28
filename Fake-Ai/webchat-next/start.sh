#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -f .env.local ]; then
  cp .env.local.example .env.local
  echo "[webchat-next] .env.local not found, copied from .env.local.example"
fi

if command -v pnpm >/dev/null 2>&1; then
  pnpm install
  pnpm dev
else
  npm install
  npm run dev
fi
