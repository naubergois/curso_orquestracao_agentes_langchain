#!/usr/bin/env bash
set -euo pipefail

# Exercício 00
#   ./run.sh                 → Docker: servidor Jupyter (Lab) com exercicio_0_sem_ecra.ipynb aberto — corres tu as células
#   ./run.sh --once          → Docker: contentor mínimo, corre main.py uma vez (saida no terminal)
#   ./run.sh --local         → venv local: main.py uma vez
#   ./run_jupyter.sh         → igual ao ./run.sh (só Jupyter)

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
  export PYTHONUNBUFFERED=1
  exec "${PYTHON}" -u main.py "$@"
}

run_docker_main_once() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Erro: instale o Docker." >&2
    exit 1
  fi
  if ! docker compose version >/dev/null 2>&1; then
    echo "Erro: instale o plugin 'docker compose'." >&2
    exit 1
  fi

  [[ -f "${ENV_FILE}" ]] || echo "Aviso: crie ${ENV_FILE} com GOOGLE_API_KEY." >&2

  # shellcheck source=/dev/null
  source "${SCRIPT_DIR}/../lib_docker_exercicios.sh"
  parar_outros_exercicios_docker "${SCRIPT_DIR}"

  cd "${SCRIPT_DIR}"
  exec docker compose run --rm --build app "$@"
}

if [[ "${1:-}" == "--local" ]]; then
  shift
  run_local "$@"
fi

if [[ "${1:-}" == "--once" ]]; then
  shift
  run_docker_main_once "$@"
fi

# --notebook / --jupyter: explícito (opcional); comportamento igual ao predefinido
if [[ "${1:-}" == "--notebook" || "${1:-}" == "--jupyter" ]]; then
  shift
fi

exec bash "${SCRIPT_DIR}/run_jupyter.sh" "$@"
