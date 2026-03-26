#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADMIN_USER="${PLONEX_ADMIN_USER:-admin}"
ADMIN_PASSWORD="${PLONEX_ADMIN_PASSWORD:-admin}"

if ! command -v plonex >/dev/null 2>&1; then
  echo "Error: plonex is not installed or not on PATH." >&2
  exit 1
fi

cd "$REPO_ROOT"

plonex init .
plonex adduser "$ADMIN_USER" "$ADMIN_PASSWORD"
plonex run scripts/bootstrap_site.py

echo
echo "Quickstart completed."
echo "Admin user: $ADMIN_USER"
echo "Run server with:"
echo "  cd $REPO_ROOT && plonex zeoclient fg"
echo "Open: http://localhost:8080/Plone"
