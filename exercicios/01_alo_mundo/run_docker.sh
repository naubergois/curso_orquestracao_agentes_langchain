#!/usr/bin/env bash
set -euo pipefail

# Porta no host por defeito 8501 (igual aos outros exercícios). Ex.: STREAMLIT_PORT=8503 ./run_docker.sh
export STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${REPO_ROOT}/.env"

if ! command -v docker >/dev/null 2>&1; then
  echo "Erro: precisa do Docker instalado e no PATH." >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Erro: precisa do plugin 'docker compose' (Docker Desktop inclui)." >&2
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Aviso: crie ${ENV_FILE} a partir de .env.example com GOOGLE_API_KEY." >&2
fi

# Parar Docker dos outros exercícios (projecto = nome da pasta, ex. 02_nerd_sarcastico)
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/../lib_docker_exercicios.sh"
parar_outros_exercicios_docker "${SCRIPT_DIR}"

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

if command -v lsof >/dev/null 2>&1; then
  libertar_porta "${STREAMLIT_PORT}"
  sleep 0.5
fi

cd "${SCRIPT_DIR}"

detache=false
compose_args=()
for a in "$@"; do
  case "$a" in
    -d | --detach) detache=true ;;
    *) compose_args+=("$a") ;;
  esac
done

if $detache; then
  if [[ ${#compose_args[@]} -gt 0 ]]; then
    docker compose up --build -d "${compose_args[@]}"
  else
    docker compose up --build -d
  fi
  echo "Serviço em segundo plano. Abra http://localhost:${STREAMLIT_PORT}"
  echo "Parar: cd \"${SCRIPT_DIR}\" && docker compose down"
  echo "Logs:  docker compose logs -f"
else
  echo "A construir e iniciar o container (Ctrl+C para parar)..."
  echo "URL: http://localhost:${STREAMLIT_PORT}"
  if [[ ${#compose_args[@]} -gt 0 ]]; then
    exec docker compose up --build "${compose_args[@]}"
  else
    exec docker compose up --build
  fi
fi
