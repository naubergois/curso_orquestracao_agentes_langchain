#!/usr/bin/env bash
set -euo pipefail
# Exercício 2 sem ecrã — Jupyter no Docker (predefinido).
# Para rebuild completo: ./run.sh --no-cache   (para outros stacks de exercícios antes: ver lib_docker_exercicios.sh)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${SCRIPT_DIR}/run_jupyter.sh" "$@"
