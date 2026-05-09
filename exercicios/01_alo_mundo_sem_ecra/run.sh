#!/usr/bin/env bash
set -euo pipefail
# Exercício 1 sem ecrã — Jupyter no Docker (predefinido). Ver run_jupyter.sh .
#   ./run.sh --no-cache [-d]  → rebuild completo da imagem Jupyter antes do up
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${SCRIPT_DIR}/run_jupyter.sh" "$@"
