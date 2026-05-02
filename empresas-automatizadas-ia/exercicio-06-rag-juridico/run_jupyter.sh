#!/usr/bin/env bash
set -euo pipefail

# Jupyter Lab sem ecrã (padrão dos exercicios/*_sem_ecra).
#   OPEN_JUPYTER_BROWSER=0 ./run.sh
#   JUPYTER_PORT=8890 ./run.sh
#   EMP_NOTEBOOK=outro.ipynb ./run.sh

export JUPYTER_PORT="${JUPYTER_PORT:-8888}"
OPEN_JUPYTER_BROWSER="${OPEN_JUPYTER_BROWSER:-1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

shopt -s nullglob
_nb_candidates=("${SCRIPT_DIR}"/exercicio_*_sem_ecra.ipynb)
if [[ ${#_nb_candidates[@]} -eq 0 ]]; then
  echo "Erro: coloque exercicio_*_sem_ecra.ipynb em ${SCRIPT_DIR}" >&2
  exit 1
fi
EMP_NOTEBOOK="${EMP_NOTEBOOK:-$(basename "${_nb_candidates[0]}")}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Erro: instale o Docker." >&2
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "Erro: instale o plugin docker compose." >&2
  exit 1
fi

[[ -f "${REPO_ROOT}/.env" ]] || echo "Aviso: crie ${REPO_ROOT}/.env com GOOGLE_API_KEY." >&2
compose_env=()
[[ -f "${REPO_ROOT}/.env" ]] && compose_env+=(--env-file "${REPO_ROOT}/.env")

# shellcheck disable=SC2295
NB_ENC="${EMP_NOTEBOOK// /%20}"
LAB_URL="http://127.0.0.1:${JUPYTER_PORT}/lab/tree/${NB_ENC}"

# shellcheck source=/dev/null
source "${SCRIPT_DIR}/../lib_docker_empresas.sh"
parar_outras_empresas_docker "${SCRIPT_DIR}"

cd "${SCRIPT_DIR}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Jupyter Lab — empresas-automatizadas-ia/$(basename "${SCRIPT_DIR}")"
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
