#!/usr/bin/env bash
# Instala dependências de todas as empresas para correr `pytest` na raiz de empresas-automatizadas-ia.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
pip install -r requirements-dev.txt
for req in exercicio-*/requirements.txt; do
  echo "=== pip install -r $req ==="
  pip install -r "$req"
done
echo "Concluído. Execute: pytest tests -m 'not integration'"
