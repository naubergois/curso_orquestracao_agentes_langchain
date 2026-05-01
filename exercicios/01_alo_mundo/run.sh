#!/usr/bin/env bash
set -euo pipefail

PORT="${STREAMLIT_PORT:-8501}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
STREAMLIT="${REPO_ROOT}/.venv/bin/streamlit"
PIP="${REPO_ROOT}/.venv/bin/pip"

if [[ "$(uname -s)" != "Darwin" && "$(uname -s)" != "Linux" ]]; then
  echo "Este script usa lsof; testado em macOS e Linux." >&2
fi

if ! command -v lsof >/dev/null 2>&1; then
  echo "Erro: precisa do comando lsof no PATH." >&2
  exit 1
fi

pids="$(lsof -ti ":${PORT}" 2>/dev/null || true)"
if [[ -n "${pids}" ]]; then
  echo "A terminar processos na porta ${PORT}: ${pids//$'\n'/ }"
  # shellcheck disable=SC2086
  kill -9 ${pids} 2>/dev/null || true
  sleep 0.5
fi

if [[ ! -x "${STREAMLIT}" ]]; then
  echo "A criar/actualizar venv e dependências em ${REPO_ROOT}/.venv ..."
  if [[ ! -x "${REPO_ROOT}/.venv/bin/python" ]]; then
    python3 -m venv "${REPO_ROOT}/.venv"
  fi
  "${PIP}" install -q -r "${SCRIPT_DIR}/requirements.txt"
fi

cd "${SCRIPT_DIR}"
echo "A iniciar Streamlit em http://localhost:${PORT}"
exec "${STREAMLIT}" run streamlit_app.py \
  --server.port "${PORT}" \
  --server.headless true \
  --browser.gatherUsageStats false "$@"
