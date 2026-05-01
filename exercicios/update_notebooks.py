#!/usr/bin/env python3
"""Atualiza cadernos Jupyter dos exercícios: limpa outputs e execution_count nas células de código.

Isto deixa os .ipynb prontos para commit (diffs legíveis) ou para distribuição sem saídas antigas.
Não altera o texto/code das células. Não precisa de Docker nem de `pip install` extra (só stdlib).

Uso:
  python3 exercicios/update_notebooks.py
  python3 exercicios/update_notebooks.py --dry-run
  python3 exercicios/update_notebooks.py --also-colab   # inclui notebooks/colab_*.ipynb
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _clean_cells(data: dict) -> int:
    """Devolve quantas células de código foram normalizadas."""
    n = 0
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        changed = False
        if cell.get("outputs"):
            cell["outputs"] = []
            changed = True
        if cell.get("execution_count") is not None:
            cell["execution_count"] = None
            changed = True
        if changed:
            n += 1
    return n


def process_notebook(path: Path, dry_run: bool) -> tuple[bool, str]:
    """Devolve (alterou?, mensagem)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return False, f"erro a ler: {e}"

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return False, f"JSON inválido: {e}"

    if data.get("nbformat") != 4:
        return False, "ignorado (nbformat != 4)"

    before = json.dumps(data, sort_keys=True)
    touched = _clean_cells(data)
    after = json.dumps(data, sort_keys=True)

    if before == after:
        return False, "já limpo"

    if dry_run:
        return True, f"seria alterado ({touched} célula(s) de código)"

    # Formato estável e legível (alinhado ao que o Jupyter costuma gravar)
    out = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    path.write_text(out, encoding="utf-8")
    return True, f"actualizado ({touched} célula(s) de código)"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Limpa outputs dos notebooks em exercicios/ (e opcionalmente notebooks/)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Só mostra que ficheiros mudariam, sem escrever.",
    )
    parser.add_argument(
        "--also-colab",
        action="store_true",
        help="Inclui também notebooks/colab*.ipynb na raiz do repositório.",
    )
    args = parser.parse_args()

    here = Path(__file__).resolve()
    if here.parent.name != "exercicios":
        print("Coloque update_notebooks.py dentro da pasta exercicios/", file=sys.stderr)
        return 1

    repo_root = here.parent.parent
    exercicios = here.parent

    paths: list[Path] = sorted(exercicios.rglob("*.ipynb"))
    # Ignorar checkpoints do Jupyter
    paths = [p for p in paths if ".ipynb_checkpoints" not in p.parts]

    if args.also_colab:
        colab_dir = repo_root / "notebooks"
        if colab_dir.is_dir():
            paths.extend(sorted(colab_dir.glob("colab*.ipynb")))
        paths = sorted(set(paths))

    if not paths:
        print("Nenhum .ipynb encontrado.")
        return 0

    changed = 0
    for p in paths:
        rel = p.relative_to(repo_root)
        did, msg = process_notebook(p, args.dry_run)
        status = "✓" if did else "·"
        print(f"{status} {rel}: {msg}")
        if did:
            changed += 1

    print(f"\nTotal: {changed}/{len(paths)} cadernos com alterações{' (dry-run)' if args.dry_run else ''}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
