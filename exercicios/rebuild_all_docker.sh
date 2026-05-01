#!/usr/bin/env bash
set -euo pipefail

# Reconstrói as imagens Docker de todos os exercícios nesta pasta (compose app + Jupyter onde existir).
# Uso: ./rebuild_all_docker.sh
#      ./rebuild_all_docker.sh --no-pull    # não fazer pull das imagens base
#      ./rebuild_all_docker.sh --no-cache   # build sem cache de camadas
#      ./rebuild_all_docker.sh --with-exemplos  # inclui exemplos/01_system_message_docker
#
# Requisitos: Docker e plugin `docker compose`.
# Nota: evita arrays vazios com `set -u` (compatível com bash 3.2 no macOS).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

USE_PULL=1
USE_NO_CACHE=0
WITH_EXEMPLOS=0
for arg in "$@"; do
  case "$arg" in
    --no-pull) USE_PULL=0 ;;
    --no-cache) USE_NO_CACHE=1 ;;
    --with-exemplos) WITH_EXEMPLOS=1 ;;
    -h | --help)
      sed -n '1,22p' "$0"
      exit 0
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "Erro: Docker não está no PATH." >&2
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "Erro: instale o plugin 'docker compose' (Docker Desktop inclui)." >&2
  exit 1
fi

# shellcheck disable=SC2164
compose_build_in() {
  local workdir="$1"
  local compose_file="$2"
  (
    cd "${workdir}"
    if [[ "${USE_NO_CACHE}" -eq 1 && "${USE_PULL}" -eq 1 ]]; then
      docker compose -f "${compose_file}" build --no-cache --pull
    elif [[ "${USE_NO_CACHE}" -eq 1 ]]; then
      docker compose -f "${compose_file}" build --no-cache
    elif [[ "${USE_PULL}" -eq 1 ]]; then
      docker compose -f "${compose_file}" build --pull
    else
      docker compose -f "${compose_file}" build
    fi
  )
}

build_stack() {
  local exercise_dir="$1"
  local compose_file="$2"
  local abs="${SCRIPT_DIR}/${exercise_dir}/${compose_file}"

  if [[ ! -f "${abs}" ]]; then
    echo "Aviso: ficheiro em falta: ${abs}" >&2
    return 0
  fi

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  docker compose build — ${exercise_dir}/${compose_file}"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  compose_build_in "${SCRIPT_DIR}/${exercise_dir}" "${compose_file}"
}

# Ordem: 00 → 01 (com / sem) → … → 09–10
build_stack 00_alo_mundo docker-compose.yml
build_stack 00_alo_mundo docker-compose.jupyter.yml
build_stack 01_alo_mundo_com_ecra docker-compose.yml
build_stack 01_alo_mundo_sem_ecra docker-compose.jupyter.yml
build_stack 02_nerd_sarcastico_com_ecra docker-compose.yml
build_stack 02_nerd_sarcastico_sem_ecra docker-compose.jupyter.yml
build_stack 03_calculadora docker-compose.yml
build_stack 03_calculadora_sem_ecra docker-compose.jupyter.yml
build_stack 04_fatores_risco_pacientes docker-compose.yml
build_stack 04_fatores_risco_pacientes_sem_ecra docker-compose.jupyter.yml
build_stack 05_prompt_templates_lcel_sem_ecra docker-compose.jupyter.yml
build_stack 06_memoria_langchain_sem_ecra docker-compose.jupyter.yml
build_stack 07_precos_clima_cotacao docker-compose.yml
build_stack 07_precos_clima_cotacao_sem_ecra docker-compose.jupyter.yml
build_stack 08_chains_complexas_sem_ecra docker-compose.jupyter.yml
build_stack 09_rag_juridico_sem_ecra docker-compose.jupyter.yml
build_stack 09_rag_juridico_com_ecra docker-compose.yml
build_stack 10_triagem_imagens_patologia_sem_ecra docker-compose.jupyter.yml
build_stack 10_triagem_imagens_patologia_com_ecra docker-compose.yml

if [[ "${WITH_EXEMPLOS}" -eq 1 ]]; then
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  docker compose build — exemplos/01_system_message_docker"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  compose_build_in "${SCRIPT_DIR}/../exemplos/01_system_message_docker" docker-compose.yml
fi

echo ""
echo "Concluído: imagens dos exercícios reconstruídas."
