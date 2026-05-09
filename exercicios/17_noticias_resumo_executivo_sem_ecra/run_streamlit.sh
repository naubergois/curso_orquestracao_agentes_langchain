#!/usr/bin/env bash
set -euo pipefail

# Tela Streamlit: boletim (ex. 17) + agente Nielsen (ex. 18).
#   ./run_streamlit.sh           → docker compose up --build -d
#   ./run_streamlit.sh --fg     → primeiro plano
#   STREAMLIT_PORT=8502 ./run_streamlit.sh

export STREAMLIT_PORT="${STREAMLIT_PORT:-8502}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${REPO_ROOT}/.env"

if ! command -v docker >/dev/null 2>&1; then
  echo "Erro: instale o Docker." >&2
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "Erro: instale o plugin docker compose." >&2
  exit 1
fi

[[ -f "${ENV_FILE}" ]] || echo "Aviso: crie ${ENV_FILE} com GOOGLE_API_KEY." >&2

# shellcheck source=/dev/null
source "${SCRIPT_DIR}/../lib_docker_exercicios.sh"
parar_outros_exercicios_docker "${SCRIPT_DIR}"

cd "${SCRIPT_DIR}"

if [[ "${1:-}" == "--fg" || "${1:-}" == "--foreground" ]]; then
  echo "Streamlit (primeiro plano): http://127.0.0.1:${STREAMLIT_PORT}"
  exec docker compose --env-file "${ENV_FILE}" -f docker-compose.streamlit.yml up --build
else
  docker compose --env-file "${ENV_FILE}" -f docker-compose.streamlit.yml up --build -d
  echo "Streamlit em execução: http://127.0.0.1:${STREAMLIT_PORT}"
  echo "Parar: cd \"${SCRIPT_DIR}\" && docker compose -f docker-compose.streamlit.yml down"
fi
