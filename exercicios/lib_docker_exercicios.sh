#!/usr/bin/env bash
# Biblioteca partilhada pelos scripts Docker dos exercícios (use: source este ficheiro).
# O projecto Compose padrão é o nome da pasta (ex.: 01_alo_mundo_com_ecra, 01_alo_mundo_sem_ecra, 03_calculadora).

_EXERCICIOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

parar_outros_exercicios_docker() {
  local este_dir
  este_dir="$(cd "$1" && pwd)"
  local outro
  for outro in "${_EXERCICIOS_ROOT}"/*/; do
    outro="$(cd "${outro}" && pwd)"
    [[ "${outro}" == "${este_dir}" ]] && continue
    local nome
    nome="$(basename "${outro}")"
    if [[ -f "${outro}/docker-compose.yml" ]]; then
      echo "A parar Docker de ${nome} (docker-compose.yml)…"
      (cd "${outro}" && docker compose down --remove-orphans 2>/dev/null) || true
    fi
    if [[ -f "${outro}/docker-compose.jupyter.yml" ]]; then
      echo "A parar Docker Jupyter de ${nome}…"
      (cd "${outro}" && docker compose -f docker-compose.jupyter.yml down --remove-orphans 2>/dev/null) || true
    fi
  done
}
