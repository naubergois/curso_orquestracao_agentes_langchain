#!/usr/bin/env bash
# Biblioteca partilhada pelos scripts Docker dos exercícios (use: source este ficheiro).
# O nome do projecto Compose padrão é o da pasta (ex.: 01_alo_mundo, 02_nerd_sarcastico).

_EXERCICIOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

parar_outros_exercicios_docker() {
  local este_dir
  este_dir="$(cd "$1" && pwd)"
  local outro
  for outro in "${_EXERCICIOS_ROOT}"/*/; do
    [[ -f "${outro}/docker-compose.yml" ]] || continue
    outro="$(cd "${outro}" && pwd)"
    [[ "${outro}" == "${este_dir}" ]] && continue
    echo "A parar Docker do exercício $(basename "${outro}") (projecto Compose padrão)…"
    (cd "${outro}" && docker compose down --remove-orphans 2>/dev/null) || true
  done
}
