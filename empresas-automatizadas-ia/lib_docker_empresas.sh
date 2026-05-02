#!/usr/bin/env bash
# Biblioteca partilhada pelos run.sh de empresas-automatizadas-ia (use: source este ficheiro).

_EMPRESAS_IA_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

parar_outras_empresas_docker() {
  local este_dir
  este_dir="$(cd "$1" && pwd)"
  local outro
  for outro in "${_EMPRESAS_IA_ROOT}"/*/; do
    [[ -d "${outro}" ]] || continue
    outro="$(cd "${outro}" && pwd)"
    [[ "${outro}" == "${este_dir}" ]] && continue
    local nome
    nome="$(basename "${outro}")"
    if [[ -f "${outro}/docker-compose.yml" ]]; then
      echo "A parar Docker de empresas-automatizadas-ia/${nome}…"
      (cd "${outro}" && docker compose down --remove-orphans 2>/dev/null) || true
    fi
    if [[ -f "${outro}/docker-compose.jupyter.yml" ]]; then
      echo "A parar Jupyter Docker de empresas-automatizadas-ia/${nome}…"
      (cd "${outro}" && docker compose -f docker-compose.jupyter.yml down --remove-orphans 2>/dev/null) || true
    fi
  done
}
