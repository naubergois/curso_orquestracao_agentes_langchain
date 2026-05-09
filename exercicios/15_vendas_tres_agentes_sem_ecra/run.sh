#!/usr/bin/env bash
set -euo pipefail
# Exercício 15 sem ecrã — Jupyter + PostgreSQL no Docker (predefinido).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${SCRIPT_DIR}/run_jupyter.sh" "$@"
