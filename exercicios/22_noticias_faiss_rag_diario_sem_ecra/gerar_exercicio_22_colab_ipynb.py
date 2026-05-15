#!/usr/bin/env python3
"""Gera `exercicio_22_colab.ipynb` a partir dos `.py` do exercício (base64 no JSON)."""

from __future__ import annotations

import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY_FILES = [
    "faiss_noticias.py",
    "agente_recolha_noticias.py",
    "agente_analista_noticias_rag.py",
]


def main() -> None:
    bundled: dict[str, str] = {}
    for name in PY_FILES:
        data = (HERE / name).read_bytes()
        bundled[name] = base64.b64encode(data).decode("ascii")

    bundled_json = json.dumps(bundled, ensure_ascii=False)
    if "'''" in bundled_json:
        raise RuntimeError("JSON inesperado: contém ''' — ajuste o delimitador do gerador.")

    cell_unpack = (
        "import base64, json, os, sys\n"
        "from pathlib import Path\n\n"
        "ROOT = Path('/content/ex22_noticias_faiss')\n"
        "ROOT.mkdir(parents=True, exist_ok=True)\n"
        "os.chdir(ROOT)\n\n"
        "_BUNDLED_JSON = r'''\n"
        + bundled_json
        + "\n'''\n"
        "_BUNDLED = json.loads(_BUNDLED_JSON)\n"
        "for fn, b64 in _BUNDLED.items():\n"
        "    (ROOT / fn).write_bytes(base64.b64decode(b64.encode('ascii')))\n\n"
        "if str(ROOT) not in sys.path:\n"
        "    sys.path.insert(0, str(ROOT))\n"
        "print('Módulos em', ROOT, ':', sorted(p.name for p in ROOT.glob('*.py')))\n"
    )

    cell_key = '''import os
try:
    from google.colab import userdata
    _k = userdata.get("GOOGLE_API_KEY")
except Exception:
    _k = None
if not (_k or "").strip():
    from getpass import getpass
    _k = getpass("Cole a GOOGLE_API_KEY (Gemini): ")
os.environ["GOOGLE_API_KEY"] = (_k or "").strip()
os.environ.setdefault("GEMINI_MODEL", "gemini-2.0-flash")
print("Chave definida:", "sim" if os.environ["GOOGLE_API_KEY"] else "não")
'''

    cell_recolha = '''from langchain_core.messages import HumanMessage

from agente_recolha_noticias import (
    config_recolha,
    criar_grafo_agente_recolha,
    ultima_resposta_assistente as ultima_recolha,
)

g_recolha = criar_grafo_agente_recolha()
cfg = config_recolha("colab-recolha")
msg = (
    "Pesquisa notícias de Portugal para hoje (manchetes e economia) "
    "e grava o índice FAISS. Se precisares, faz uma última consulta abrangente antes de gravar."
)
out = g_recolha.invoke({"messages": [HumanMessage(content=msg)]}, cfg)
print(ultima_recolha(out))
'''

    cell_analista = '''from langchain_core.messages import HumanMessage

from agente_analista_noticias_rag import (
    config_analista,
    criar_grafo_agente_analista,
    ultima_resposta_assistente as ultima_analista,
)

g_rag = criar_grafo_agente_analista()
cfg2 = config_analista("colab-rag")
pergunta = (
    "Com base nas notícias indexadas, resume os temas principais e indica "
    "dois riscos ou incertezas para um decisor. Usa a ferramenta de recuperação."
)
out2 = g_rag.invoke({"messages": [HumanMessage(content=pergunta)]}, cfg2)
print(ultima_analista(out2))
'''

    cell_pip = """import subprocess, sys
pkgs = [
    "python-dotenv>=1,<2",
    "pydantic>=2.7,<3",
    "langchain-core>=0.3",
    "langchain-community>=0.3",
    "langchain-google-genai>=2",
    "langchain-text-splitters>=0.3",
    "langgraph>=0.2,<2",
    "faiss-cpu>=1.8,<2",
    "ddgs>=9,<11",
]
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *pkgs])
print("pip ok")
"""

    md = """# Ex. 22 — Google **Colab** (notícias + FAISS + RAG)

1. **Runtime → Run all** (ou célula a célula de cima para baixo).
2. **Chave Gemini:** no Colab, vá a **ícone de chaves → Secrets** e crie `GOOGLE_API_KEY` com a sua chave da [Google AI Studio](https://aistudio.google.com/apikey).  
   Se não usar Secrets, a célula seguinte pede a chave em modo oculto (`getpass`).
3. **Runtime com rede:** o host precisa de Internet (DuckDuckGo + API Gemini).
4. O índice FAISS fica em `/content/ex22_noticias_faiss/faiss_noticias_index/` durante a sessão (perde-se ao fechar o runtime, salvo que copie para o Drive).

**Nota:** este caderno é gerado por `gerar_exercicio_22_colab_ipynb.py` no repositório; após alterar os `.py`, volte a correr o script para actualizar o Colab.
"""

    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11.0"},
        },
        "cells": [
            {"cell_type": "markdown", "id": "m0", "metadata": {}, "source": md.splitlines(keepends=True)},
            {
                "cell_type": "code",
                "id": "c_pip",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [line + "\n" for line in cell_pip.strip().split("\n")],
            },
            {
                "cell_type": "code",
                "id": "c_unpack",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [line + "\n" for line in cell_unpack.strip().split("\n")],
            },
            {
                "cell_type": "code",
                "id": "c_key",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [line + "\n" for line in cell_key.strip().split("\n")],
            },
            {
                "cell_type": "code",
                "id": "c_recolha",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [line + "\n" for line in cell_recolha.strip().split("\n")],
            },
            {
                "cell_type": "code",
                "id": "c_analista",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [line + "\n" for line in cell_analista.strip().split("\n")],
            },
        ],
    }

    out = HERE / "exercicio_22_colab.ipynb"
    out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Escrito:", out)


if __name__ == "__main__":
    main()
