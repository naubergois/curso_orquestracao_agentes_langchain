#!/usr/bin/env bash
set -euo pipefail
# Limpa outputs dos .ipynb em exercicios/ (ver update_notebooks.py).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/update_notebooks.py" "$@"
