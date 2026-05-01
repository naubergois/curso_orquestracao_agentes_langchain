#!/usr/bin/env bash
set -euo pipefail
# Exercício 10 com ecrã — Streamlit + MongoDB (Docker). Ver run.ps1 / docker-compose.yml .
export STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"
export MONGO_EX10_PORT="${MONGO_EX10_PORT:-27018}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/../lib_docker_exercicios.sh"
parar_outros_exercicios_docker "${SCRIPT_DIR}"
[[ -f "${REPO_ROOT}/.env" ]] || echo "Aviso: ${REPO_ROOT}/.env" >&2
cd "${SCRIPT_DIR}"
docker compose up --build -d
echo "http://localhost:${STREAMLIT_PORT} — Mongo na porta host ${MONGO_EX10_PORT}"
echo "Parar: docker compose down"
