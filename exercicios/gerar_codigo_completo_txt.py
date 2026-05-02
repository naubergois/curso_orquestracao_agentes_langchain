#!/usr/bin/env python3
"""Gera `CODIGO_COMPLETO.txt` na raiz de cada pasta `exercicios/NN_*`.

Pastas em `EXTRA_CODIGO_COMPLETO_DIRS` (ex.: `rag_auditoria_rostos_sem_ecra`) geram
também `CODIGO_COMPLETO.md` com o mesmo corpo num bloco `~~~text`.

Inclui: `requirements.txt` (se existir), todos os `*.py` desse nível, e `*.ipynb`
do mesmo nível (células markdown comentadas com `# `, células código em bruto).
Exclui `.ipynb_checkpoints` e subpastas.

Uso (na raiz do repositório):
  python exercicios/gerar_codigo_completo_txt.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

BANNER = """# ================================================================================
# CODIGO_COMPLETO.txt — export estático do exercício (leitura offline / impressão)
# Gerado por: exercicios/gerar_codigo_completo_txt.py
# Não editar à mão: voltar a correr o script após alterar .py ou .ipynb.
# ================================================================================

"""

EXERCISE_DIR_PATTERN = re.compile(r"^\d\d_.+")

# Pastas sem prefixo `NN_` que também exportam CODIGO_COMPLETO (ex.: RAG auditoria isolado).
EXTRA_CODIGO_COMPLETO_DIRS = ("rag_auditoria_rostos_sem_ecra",)

PY_ORDER = ("main.py", "agent.py", "streamlit_app.py")


def _cell_source_to_str(source) -> str:
    if isinstance(source, list):
        return "".join(source)
    return str(source)


def _render_notebook(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    lines: list[str] = []
    lines.append(f"\n{'=' * 80}\n")
    lines.append(f"# FICHEIRO: {path.name}\n")
    lines.append(f"{'=' * 80}\n\n")
    for i, cell in enumerate(data.get("cells", [])):
        ctype = cell.get("cell_type", "?")
        src = _cell_source_to_str(cell.get("source", "")).rstrip()
        if ctype == "markdown":
            lines.append(f"# --- Célula {i} (markdown) ---\n")
            for line in src.splitlines():
                lines.append(f"# {line}\n")
            lines.append("\n")
        elif ctype == "code":
            lines.append(f"# --- Célula {i} (código) ---\n")
            if src:
                lines.append(src)
                lines.append("\n\n")
        else:
            lines.append(f"# --- Célula {i} ({ctype}) ---\n# (omitido)\n\n")
    return "".join(lines)


def _sorted_py(files: list[Path]) -> list[Path]:
    names = {p.name: p for p in files}
    ordered: list[Path] = []
    for n in PY_ORDER:
        if n in names:
            ordered.append(names.pop(n))
    for p in sorted(names.values(), key=lambda x: x.name):
        ordered.append(p)
    return ordered


def generate_for_exercise_dir(ex_dir: Path) -> str:
    parts: list[str] = [BANNER, f"# Pasta: {ex_dir.name}\n\n"]

    req = ex_dir / "requirements.txt"
    if req.is_file():
        parts.append(f"{ '=' * 80}\n# FICHEIRO: requirements.txt\n{ '=' * 80}\n\n")
        parts.append(req.read_text(encoding="utf-8").rstrip())
        parts.append("\n\n")

    py_files = sorted(ex_dir.glob("*.py"))
    for p in _sorted_py(py_files):
        parts.append(f"{ '=' * 80}\n# FICHEIRO: {p.name}\n{ '=' * 80}\n\n")
        parts.append(p.read_text(encoding="utf-8").rstrip())
        parts.append("\n\n")

    for nb in sorted(ex_dir.glob("*.ipynb")):
        parts.append(_render_notebook(nb))

    return "".join(parts).rstrip() + "\n"


def generate_codigo_completo_markdown(ex_dir: Path, titulo: str) -> str:
    """Markdown com o mesmo corpo que CODIGO_COMPLETO.txt (bloco `~~~text` para evitar conflitos)."""
    corpo = generate_for_exercise_dir(ex_dir)
    safe = corpo.replace("~~~", "~ ~ ~")
    return (
        f"# {titulo}\n\n"
        "Export estático — mesmo conteúdo que `CODIGO_COMPLETO.txt`. "
        "Gerado por `exercicios/gerar_codigo_completo_txt.py`.\n\n"
        f"~~~text\n{safe}\n~~~\n"
    )


def main() -> None:
    root = Path(__file__).resolve().parent
    exercise_dirs = sorted(
        d for d in root.iterdir() if d.is_dir() and EXERCISE_DIR_PATTERN.match(d.name)
    )
    extra_dirs = [root / name for name in EXTRA_CODIGO_COMPLETO_DIRS if (root / name).is_dir()]

    if not exercise_dirs and not extra_dirs:
        raise SystemExit("Nenhuma pasta NN_* nem extras encontrada em exercicios/.")

    for ex_dir in exercise_dirs:
        out = ex_dir / "CODIGO_COMPLETO.txt"
        text = generate_for_exercise_dir(ex_dir)
        out.write_text(text, encoding="utf-8")
        print(f"Escrito: {out.relative_to(root.parent)}")

    for ex_dir in extra_dirs:
        text = generate_for_exercise_dir(ex_dir)
        (ex_dir / "CODIGO_COMPLETO.txt").write_text(text, encoding="utf-8")
        print(f"Escrito: {(ex_dir / 'CODIGO_COMPLETO.txt').relative_to(root.parent)}")
        md_path = ex_dir / "CODIGO_COMPLETO.md"
        titulo = (
            "CODIGO_COMPLETO — RAG multimodal (relatórios + rostos LFW + achados estruturados)"
            if ex_dir.name == "rag_auditoria_rostos_sem_ecra"
            else f"CODIGO_COMPLETO — {ex_dir.name}"
        )
        md_path.write_text(generate_codigo_completo_markdown(ex_dir, titulo), encoding="utf-8")
        print(f"Escrito: {md_path.relative_to(root.parent)}")


if __name__ == "__main__":
    main()
