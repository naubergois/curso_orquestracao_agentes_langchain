#!/usr/bin/env bash
set -euo pipefail

# Exercício 3 — sem ecrã (Jupyter no Docker).
#   EX03_NOTEBOOK=outro.ipynb
#   OPEN_JUPYTER_BROWSER=0

export JUPYTER_PORT="${JUPYTER_PORT:-8888}"
OPEN_JUPYTER_BROWSER="${OPEN_JUPYTER_BROWSER:-1}"
EX03_NOTEBOOK="${EX03_NOTEBOOK:-exercicio_3_sem_ecra.ipynb}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "Erro: instale o Docker." >&2
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "Erro: instale o plugin docker compose." >&2
  exit 1
fi

[[ -f "${REPO_ROOT}/.env" ]] || echo "Aviso: crie ${REPO_ROOT}/.env com GOOGLE_API_KEY." >&2
ENV_FILE="${REPO_ROOT}/.env"
compose_env=()
[[ -f "${ENV_FILE}" ]] && compose_env+=(--env-file "${ENV_FILE}")

# shellcheck disable=SC2295
NB_ENC="${EX03_NOTEBOOK// /%20}"
LAB_URL="http://127.0.0.1:${JUPYTER_PORT}/lab/tree/${NB_ENC}"

# shellcheck source=/dev/null
source "${SCRIPT_DIR}/../lib_docker_exercicios.sh"
parar_outros_exercicios_docker "${SCRIPT_DIR}"

cd "${SCRIPT_DIR}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Jupyter Lab — ex. 3 sem ecrã (sem token: só localhost)"
echo "  URL:  ${LAB_URL}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Parar: cd \"${SCRIPT_DIR}\" && docker compose -f docker-compose.jupyter.yml down"
echo ""

_abrir_browser() {
  [[ "${OPEN_JUPYTER_BROWSER}" == "1" ]] || return 0
  local url="$1"
  if command -v open >/dev/null 2>&1; then
    open "${url}" 2>/dev/null || true
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "${url}" 2>/dev/null || true
  fi
}

( sleep 7 && _abrir_browser "${LAB_URL}" ) &

docker compose "${compose_env[@]}" -f docker-compose.jupyter.yml up --build "$@"
