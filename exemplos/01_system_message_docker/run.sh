#!/usr/bin/env bash
set -euo pipefail

# Exemplo sem UI: SystemMessage + HumanMessage. Docker corre uma vez e imprime no stdout.
#   ./run.sh
#   ./run.sh --local
#   ./run.sh --local "Qual é a capital do Chile?"
#   ./run.sh "Qual é a capital do Chile?"   # Docker (argumentos repassados ao main.py)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${REPO_ROOT}/.env"
PYTHON="${REPO_ROOT}/.venv/bin/python"
PIP="${REPO_ROOT}/.venv/bin/pip"

run_local() {
  if [[ ! -x "${PYTHON}" ]]; then
    if ! command -v python3 >/dev/null 2>&1; then
      echo "Erro: precisa de python3 no PATH." >&2
      exit 1
    fi
    python3 -m venv "${REPO_ROOT}/.venv"
  fi
  "${PIP}" install -q -r "${SCRIPT_DIR}/requirements.txt"
  cd "${SCRIPT_DIR}"
  exec "${PYTHON}" -u main.py "$@"
}

run_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Erro: instale o Docker." >&2
    exit 1
  fi
  if ! docker compose version >/dev/null 2>&1; then
    echo "Erro: instale o plugin 'docker compose'." >&2
    exit 1
  fi

  [[ -f "${ENV_FILE}" ]] || echo "Aviso: crie ${ENV_FILE} com GOOGLE_API_KEY." >&2

  cd "${SCRIPT_DIR}"
  exec docker compose run --rm --build app "$@"
}

if [[ "${1:-}" == "--local" ]]; then
  shift
  run_local "$@"
else
  run_docker "$@"
fi
