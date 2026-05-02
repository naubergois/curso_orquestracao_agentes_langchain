#!/usr/bin/env python3
"""Gera exercicio_13_sem_ecra.ipynb — PDF + chunks + agente ReAct."""

from __future__ import annotations

import json
from pathlib import Path


def md(s: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [s]}


def code(s: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [s],
    }


META = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"},
}

INTRO = """# Exercício 13 — agente **ReAct** sobre PDFs *chunkados*

Combina o fluxo do **exercício 12** (PDF → texto → splits) com um **agente LangGraph** que só pode **ler o corpus através de ferramentas**:

- **`estatisticas_corpus`** — contagens e nomes dos PDFs indexados em memória.
- **`procurar_trechos`** — recuperação lexical simples (sem vector DB).
- **`ler_chunk_completo`** — leitura integral de um chunk por `id`.

**Porquê tools?** O modelo não deve «adivinhar» o conteúdo dos PDFs; deve **consultar** os troços indexados.

**Docker:** `./run.sh`. Chave **`GOOGLE_API_KEY`** no `.env` na raiz. Modelo: **`GEMINI_MODEL_EX13`** ou **`GEMINI_MODEL`** (Gemini 2.x)."""

C1 = r"""import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

ROOT = Path.cwd().resolve()
REPO = ROOT.parent.parent
load_dotenv(REPO / ".env", override=False)

key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not key:
    raise RuntimeError("Defina GOOGLE_API_KEY no `.env` na raiz do repositório.")
os.environ.setdefault("GOOGLE_API_KEY", key)

_DEFAULT = "gemini-2.0-flash"
nome_modelo = (os.environ.get("GEMINI_MODEL_EX13") or os.environ.get("GEMINI_MODEL") or _DEFAULT).strip()
nome_modelo = nome_modelo.removeprefix("models/")
if nome_modelo.startswith("gemini-1.5"):
    print("Aviso: `gemini-1.5*` → `gemini-2.0-flash`.", file=sys.stderr, flush=True)
    nome_modelo = _DEFAULT


def build_chat_model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=nome_modelo, temperature=0.2)


DATA = ROOT / "data" / "pdfs_sample"
DATA.mkdir(parents=True, exist_ok=True)
print("Modelo:", nome_modelo)
print("PDFs em:", DATA)
"""

C2 = r"""# 1) Gerar PDFs fictícios (mesmo género que no ex. 12)

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _xml(txt: str) -> str:
    return (
        txt.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def escrever_pdf(path: Path, titulo_capa: str, blocos: list[tuple[str, str]]) -> None:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    story = []
    story.append(Paragraph(_xml(titulo_capa), styles["Title"]))
    story.append(Spacer(1, 16))
    for subtitulo, corpo in blocos:
        story.append(Paragraph(_xml(subtitulo), styles["Heading2"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(_xml(corpo), styles["Normal"]))
        story.append(Spacer(1, 14))
    doc.build(story)


pol = [
    (
        "Retenção",
        "Períodos de retenção documentados no sistema de arquivo; eliminação segura após "
        "validação jurídica. RH e payroll mantêm cópias mínimas para litígios laborais.",
    ),
    (
        "Acessos",
        "Perfis revistos trimestralmente. Contas de serviço para integrações SAP "
        "registadas com titular de negócio e ticket de mudança.",
    ),
]

ata = [
    (
        "Payroll off-cycle",
        "Discussão sobre lançamentos fora do ciclo normal; pedido de reconciliação ao "
        "controlling e junção de prints de aprovação no dossier de auditoria.",
    ),
    (
        "RH",
        "Confirmação de formações obrigatórias e lista de presenças digitalizada para "
        "cruzar com picagens incompletas.",
    ),
]

escrever_pdf(DATA / "politica_curta.pdf", "Política (fictícia)", pol)
escrever_pdf(DATA / "ata_curta.pdf", "Ata (fictícia)", ata)
sorted(p.name for p in DATA.glob("*.pdf"))
"""

C3 = r"""# 2) Extrair texto e construir lista global de chunks `CHUNKS`

import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


def texto_por_pagina(pdf_path: Path) -> list[str]:
    r = PdfReader(str(pdf_path))
    return [(p.extract_text() or "").strip() for p in r.pages]


registos: list[dict] = []
for pdf in sorted(DATA.glob("*.pdf")):
    for idx, pg in enumerate(texto_por_pagina(pdf), start=1):
        registos.append({"fonte": pdf.name, "pagina": idx, "texto": pg})

splitter = RecursiveCharacterTextSplitter(chunk_size=380, chunk_overlap=70)

CHUNKS: list[dict] = []
cid = 0
for r in registos:
    t = re.sub(r"\s+", " ", r["texto"]).strip()
    if len(t) < 20:
        continue
    for piece in splitter.split_text(t):
        CHUNKS.append(
            {"id": cid, "text": piece, "fonte": r["fonte"], "pagina": r["pagina"]}
        )
        cid += 1

len(CHUNKS), CHUNKS[0]
"""

C4 = r"""# 3) Ferramentas + grafo ReAct (LangGraph)

import re

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent


@tool
def estatisticas_corpus() -> str:
    "Resumo do índice em memória: número de chunks e nomes dos PDFs."
    fonts = sorted({c["fonte"] for c in CHUNKS})
    return f"Total de chunks: {len(CHUNKS)}. Ficheiros: {', '.join(fonts)}."


@tool
def procurar_trechos(consulta: str, limite: int = 5) -> str:
    "Recupera trechos por pontuação simples de palavras da consulta (sem embeddings)."
    palavras = [w for w in re.findall(r"\w+", consulta.lower()) if len(w) > 2]
    if not palavras:
        return "Indique palavras mais específicas na consulta."
    try:
        limite = int(float(limite))
    except (TypeError, ValueError):
        limite = 5
    limite = max(1, min(limite, 12))
    scored: list[tuple[int, dict]] = []
    for c in CHUNKS:
        tx = c["text"].lower()
        sc = sum(tx.count(w) for w in palavras)
        if sc:
            scored.append((sc, c))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        return "Nenhum trecho com essas palavras."
    linhas = []
    for sc, c in scored[:limite]:
        preview = c["text"].replace("\n", " ")[:340]
        linhas.append(
            f"id={c['id']} score={sc} | {c['fonte']} p.{c['pagina']} | {preview}..."
        )
    return "\n---\n".join(linhas)


@tool
def ler_chunk_completo(identificador: int) -> str:
    "Devolve o texto completo de um chunk pelo seu id numérico."
    for c in CHUNKS:
        if c["id"] == int(identificador):
            return f"[{c['fonte']} página {c['pagina']}]\n{c['text']}"
    return "Id inexistente. Use procurar_trechos primeiro."


def build_graph():
    return create_react_agent(
        build_chat_model(),
        tools=[estatisticas_corpus, procurar_trechos, ler_chunk_completo],
        checkpointer=MemorySaver(),
    )


graph = build_graph()
print("Ferramentas registadas:", [estatisticas_corpus.name, procurar_trechos.name, ler_chunk_completo.name])
"""

C5 = r"""# 4) Pergunta de demonstração (o agente deve usar tools)

cfg = {"configurable": {"thread_id": "thread-pdf-agent"}}

out = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content=(
                    "Quantos chunks existem no corpus? Depois procura menções a payroll ou RH "
                    "e resume o que está escrito, citando ids dos trechos que usaste."
                )
            )
        ]
    },
    config=cfg,
)

print(out["messages"][-1].content)
"""

cells = [
    md(INTRO),
    code(C1),
    code(C2),
    code(C3),
    code(C4),
    code(C5),
]

nb = {"nbformat": 4, "nbformat_minor": 5, "metadata": META, "cells": cells}

Path(__file__).resolve().parent.joinpath("exercicio_13_sem_ecra.ipynb").write_text(
    json.dumps(nb, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("Notebook escrito.")
