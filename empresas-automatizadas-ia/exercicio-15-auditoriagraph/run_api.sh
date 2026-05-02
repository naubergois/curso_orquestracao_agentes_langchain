#!/usr/bin/env bash
set -euo pipefail

# API FastAPI opcional (porta 8000).
#   ./run_api.sh              → docker compose up --build -d
#   ./run_api.sh --fg         → Docker em primeiro plano
#   ./run_api.sh --local      → Uvicorn com venv na raiz do repositório do curso
#
#   APP_PORT=8001 ./run_api.sh  → altera mapeamento local (ajuste também docker-compose se necessário)

export APP_PORT="${APP_PORT:-8000}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_REPO="${REPO_ROOT}/.env"
VENV_PY="${REPO_ROOT}/.venv/bin/python"
VENV_PIP="${REPO_ROOT}/.venv/bin/pip"

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
    echo "Erro: precisa do lsof no PATH para --local." >&2
    exit 1
  fi
  libertar_porta "${APP_PORT}"
  sleep 0.5
  if [[ ! -x "${VENV_PY}" ]]; then
    python3 -m venv "${REPO_ROOT}/.venv"
  fi
  "${VENV_PIP}" install -q -r "${SCRIPT_DIR}/requirements.txt"
  cd "${SCRIPT_DIR}"
  echo "Local (venv): http://localhost:${APP_PORT}"
  exec "${VENV_PY}" -m uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT}"
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

  if [[ ! -f "${ENV_REPO}" ]]; then
    echo "Aviso: crie ${ENV_REPO} com GOOGLE_API_KEY (o Compose usa ../../.env a partir desta pasta)." >&2
  fi

  # shellcheck source=/dev/null
  source "${SCRIPT_DIR}/../lib_docker_empresas.sh"
  parar_outras_empresas_docker "${SCRIPT_DIR}"

  if command -v lsof >/dev/null 2>&1; then
    libertar_porta "${APP_PORT}"
    sleep 0.5
  fi

  cd "${SCRIPT_DIR}"
  if $foreground; then
    echo "Docker (primeiro plano): http://localhost:${APP_PORT}"
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
    echo "Docker em execução: http://localhost:${APP_PORT}"
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
