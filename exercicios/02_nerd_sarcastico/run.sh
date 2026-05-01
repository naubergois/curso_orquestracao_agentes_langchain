#!/usr/bin/env bash
set -euo pipefail

# Predefinição: Docker (detached). Opções:
#   ./run.sh              → docker compose up --build -d
#   ./run.sh --fg         → docker em primeiro plano (logs no terminal)
#   ./run.sh --local      → Streamlit com venv na raiz do repo (sem Docker)
#   STREAMLIT_PORT=8503 ./run.sh  (todos os exercícios usam 8501 por defeito)

export STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${REPO_ROOT}/.env"
STREAMLIT="${REPO_ROOT}/.venv/bin/streamlit"
PIP="${REPO_ROOT}/.venv/bin/pip"

libertar_porta() {
  local porta="$1"
  if ! command -v lsof >/dev/null 2>&1; then
    return 0
  fi
  local pids
  pids="$(lsof -ti ":${porta}" 2>/dev/null || true)"
  if [[ -n "${pids}" ]]; then
    echo "A libertar porta ${porta}: ${pids//$'\n'/ }"
    # shellcheck disable=SC2086
    kill -9 ${pids} 2>/dev/null || true
  fi
}

run_local() {
  if ! command -v lsof >/dev/null 2>&1; then
    echo "Erro: precisa do lsof no PATH." >&2
    exit 1
  fi
  libertar_porta "${STREAMLIT_PORT}"
  sleep 0.5
  if [[ ! -x "${STREAMLIT}" ]]; then
    if [[ ! -x "${REPO_ROOT}/.venv/bin/python" ]]; then
      python3 -m venv "${REPO_ROOT}/.venv"
    fi
    "${PIP}" install -q -r "${SCRIPT_DIR}/requirements.txt"
  fi
  cd "${SCRIPT_DIR}"
  echo "Local (venv): http://localhost:${STREAMLIT_PORT}"
  exec "${STREAMLIT}" run streamlit_app.py \
    --server.port "${STREAMLIT_PORT}" \
    --server.headless true \
    --browser.gatherUsageStats false "$@"
}

run_docker() {
  local foreground=false
  local compose_extra=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --fg | --foreground)
        foreground=true
        shift
        ;;
      *)
        compose_extra+=("$1")
        shift
        ;;
    esac
  done

  if ! command -v docker >/dev/null 2>&1; then
    echo "Erro: instale o Docker." >&2
    exit 1
  fi
  if ! docker compose version >/dev/null 2>&1; then
    echo "Erro: instale o plugin 'docker compose'." >&2
    exit 1
  fi

  [[ -f "${ENV_FILE}" ]] || echo "Aviso: crie ${ENV_FILE} com GOOGLE_API_KEY." >&2

  # Parar stacks dos outros exercícios (nome do projecto = pasta do exercício)
  # shellcheck source=/dev/null
  source "${SCRIPT_DIR}/../lib_docker_exercicios.sh"
  parar_outros_exercicios_docker "${SCRIPT_DIR}"

  if command -v lsof >/dev/null 2>&1; then
    libertar_porta "${STREAMLIT_PORT}"
    sleep 0.5
  fi

  cd "${SCRIPT_DIR}"
  if $foreground; then
    echo "Docker (primeiro plano): http://localhost:${STREAMLIT_PORT}"
    if [[ ${#compose_extra[@]} -gt 0 ]]; then
      exec docker compose up --build "${compose_extra[@]}"
    else
      exec docker compose up --build
    fi
  else
    if [[ ${#compose_extra[@]} -gt 0 ]]; then
      docker compose up --build -d "${compose_extra[@]}"
    else
      docker compose up --build -d
    fi
    echo "Docker em execução: http://localhost:${STREAMLIT_PORT}"
    echo "Parar: cd \"${SCRIPT_DIR}\" && docker compose down"
    echo "Logs:  docker compose logs -f"
  fi
}

if [[ "${1:-}" == "--local" ]]; then
  shift
  run_local "$@"
else
  run_docker "$@"
fi
