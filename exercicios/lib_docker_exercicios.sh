#!/usr/bin/env bash
# Biblioteca partilhada pelos scripts Docker dos exercícios (use: source este ficheiro).
# parar_outros_exercicios_docker: faz `docker compose down` em todas as pastas irmãs em exercicios/*/
#   com docker-compose.yml ou docker-compose.jupyter.yml — exceto a pasta atual. Não afeta Docker fora de exercicios/.

_EXERCICIOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

parar_outros_exercicios_docker() {
  local este_dir
  este_dir="$(cd "$1" && pwd)"
  local outro nome
  # `find` evita falhas de glob em zsh (nomatch) e quando não há subpastas.
  while IFS= read -r -d '' outro; do
    outro="$(cd "${outro}" && pwd)"
    [[ "${outro}" == "${este_dir}" ]] && continue
    nome="$(basename "${outro}")"
    if [[ -f "${outro}/docker-compose.yml" ]]; then
      echo "A parar Docker de ${nome} (docker-compose.yml)…"
      (cd "${outro}" && docker compose down --remove-orphans 2>/dev/null) || true
    fi
    if [[ -f "${outro}/docker-compose.jupyter.yml" ]]; then
      echo "A parar Docker Jupyter de ${nome}…"
      (cd "${outro}" && docker compose -f docker-compose.jupyter.yml down --remove-orphans 2>/dev/null) || true
    fi
  done < <(find "${_EXERCICIOS_ROOT}" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
}
