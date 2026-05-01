"""Agente ReAct (LangGraph) que gera texto pedagógico e grava PDFs jurídicos fictícios (ex. 9).

Requer rede e `GOOGLE_API_KEY` / `GEMINI_API_KEY`. A tool `publicar_pdf_conceito` delega em
`gerar_pdfs_conceitos.escrever_pdf_texto_plano` (HTML escapado).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

_DIRETORIO_PDFS: Path | None = None


def definir_diretorio_pdfs(p: Path) -> None:
    global _DIRETORIO_PDFS
    _DIRETORIO_PDFS = Path(p).resolve()


@tool
def publicar_pdf_conceito(slug: str, titulo: str, texto_plano: str) -> str:
    """Grava `slug.pdf` na pasta configurada. Material **fictício** de estudo, PT-PT.

    Args:
        slug: nome do ficheiro sem extensão (ex.: negocio_juridico). Minúsculas, `_` permitido.
        titulo: título (aparece em negrito).
        texto_plano: 2–4 parágrafos separados por **uma linha em branco**; texto simples, sem HTML.
    """
    if _DIRETORIO_PDFS is None:
        return "Erro interno: diretório PDF não configurado."
    slug_clean = slug.strip().lower().replace(" ", "_")
    safe = slug_clean.replace("_", "")
    if not safe or not safe.isalnum():
        return "Slug inválido."
    from gerar_pdfs_conceitos import escrever_pdf_texto_plano

    out = escrever_pdf_texto_plano(
        _DIRETORIO_PDFS,
        slug_clean,
        titulo.strip(),
        texto_plano.strip(),
    )
    return f"PDF gravado: {out.name}"


def _load_env() -> None:
    here = Path(__file__).resolve()
    for d in (here.parent, *here.parents):
        env = d / ".env"
        if env.is_file():
            load_dotenv(env, override=False)
            return


def _ensure_key() -> None:
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        raise RuntimeError("Defina GOOGLE_API_KEY ou GEMINI_API_KEY para o agente gerador.")


def build_graph():
    """Grafo ReAct com memória em RAM (`thread_id` distingue corridas)."""
    _load_env()
    _ensure_key()
    ex = Path(__file__).resolve().parent.parent
    if str(ex) not in sys.path:
        sys.path.insert(0, str(ex))
    from lib_llm_fallback import gemini_model_candidates, make_gemini_chat_with_runtime_fallback

    prim = (
        os.environ.get("GEMINI_MODEL_EX09")
        or os.environ.get("GEMINI_MODEL")
        or "gemini-2.0-flash"
    ).strip()
    candidatos = gemini_model_candidates(primary=prim)
    llm = make_gemini_chat_with_runtime_fallback(candidatos, temperature=0.35)
    return create_react_agent(
        llm,
        tools=[publicar_pdf_conceito],
        checkpointer=MemorySaver(),
    )


_INSTRUCAO_LOTE = """Gera **5 PDFs pedagógicos** chamando `publicar_pdf_conceito` **5 vezes** (uma chamada por ficheiro).

Usa **exactamente** estes slugs (1.º argumento):
1) negocio_juridico — negócio jurídico (noção geral, requisitos típicos).
2) contrato — contrato e liberdade contratual.
3) responsabilidade_civil — responsabilidade civil introdutória.
4) prescricao_caducidade — prescrição vs caducidade (visão geral).
5) boa_fe — boa-fé nas relações jurídicas.

Em cada chamada: `titulo` curto; `texto_plano` com 2–3 parágrafos separados por uma linha em branco; português europeu; não inventes artigos de lei nem acórdãos; indica tom de material de apoio a estudo.
No fim, uma frase a confirmar que os cinco ficheiros foram gravados."""


_ESPERADOS = frozenset(
    {
        "negocio_juridico.pdf",
        "contrato.pdf",
        "responsabilidade_civil.pdf",
        "prescricao_caducidade.pdf",
        "boa_fe.pdf",
    }
)


def executar_geracao_pdfs_via_agente(
    directorio: Path,
    *,
    thread_id: str = "ex09-agente-pdfs",
) -> list[Path]:
    """Invoca o agente até existirem os cinco PDFs esperados (ou falha com mensagem clara)."""
    definir_diretorio_pdfs(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    graph = build_graph()
    graph.invoke(
        {"messages": [HumanMessage(content=_INSTRUCAO_LOTE)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    presentes = {p.name for p in directorio.glob("*.pdf")}
    if not _ESPERADOS <= presentes:
        faltam = sorted(_ESPERADOS - presentes)
        raise RuntimeError(
            f"O agente não gravou todos os PDFs. Em falta: {faltam}. "
            "Corra de novo ou use `gerar_todos_pdfs` (conteúdo estático)."
        )
    return [(directorio / n).resolve() for n in sorted(_ESPERADOS)]
