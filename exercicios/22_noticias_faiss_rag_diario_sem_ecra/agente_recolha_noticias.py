"""Agente ReAct: pesquisa Web (DuckDuckGo) e gravação do resultado em FAISS."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from faiss_noticias import indexar_ultima_pesquisa_em_faiss, pesquisa_duckduckgo_texto


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_local_env()


def _modelo() -> str:
    return (os.environ.get("GEMINI_MODEL_EX22") or os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").strip()


def _garantir_chave_api() -> None:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Defina GOOGLE_API_KEY ou GEMINI_API_KEY no `.env` na raiz do repositório.")
    os.environ.setdefault("GOOGLE_API_KEY", key)


@tool
def pesquisar_noticias_web_para_indexacao(consulta: str) -> str:
    """Pesquisa na Web via DuckDuckGo (snippets e links). Use consultas curtas em português, ex.: «notícias Portugal hoje», «economia Europa». Requer rede."""
    return pesquisa_duckduckgo_texto(consulta.strip())


@tool
def gravar_ultima_pesquisa_no_indice_faiss() -> str:
    """Indexa em FAISS o texto da **última** pesquisa Web feita nesta sessão (substitui o índice anterior na pasta do exercício). Chame **depois** de `pesquisar_noticias_web_para_indexacao`."""
    n = indexar_ultima_pesquisa_em_faiss(substituir=True)
    return f"FAISS actualizado: {n} vectores (chunks) gravados."


_SYSTEM = """És um **editor de agência** que prepara material bruto para um sistema RAG.

Fluxo:
1. Usa `pesquisar_noticias_web_para_indexacao` com **1 a 4** consultas complementares para cobrir o dia (política, economia, sociedade — conforme o pedido do utilizador).
2. Quando tiveres trechos suficientes, chama **uma vez** `gravar_ultima_pesquisa_no_indice_faiss` para gravar **apenas a última** pesquisa em memória intermédia.

**Atenção:** a tool de gravação indexa só o resultado da **última** chamada à pesquisa. Se precisares de fundir várias pesquisas num único índice, faz uma **última** pesquisa mais abrangente (ex.: «resumo notícias Portugal hoje manchetes») e grava em seguida.

Regras:
- Não inventes URLs nem factos que não apareçam nos snippets.
- Resposta final ao utilizador: resumo curto do que foi gravado e para que temas serve o índice. Português europeu."""


def criar_grafo_agente_recolha() -> Any:
    _garantir_chave_api()
    llm = ChatGoogleGenerativeAI(model=_modelo(), temperature=0.25)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return create_react_agent(
        llm,
        tools=[pesquisar_noticias_web_para_indexacao, gravar_ultima_pesquisa_no_indice_faiss],
        prompt=prompt,
        checkpointer=MemorySaver(),
    )


def config_recolha(thread_id: str = "ex22-recolha-noticias") -> dict:
    return {"configurable": {"thread_id": thread_id}}


def ultima_resposta_assistente(resultado: dict) -> str:
    msgs = resultado.get("messages") or []
    for m in reversed(msgs):
        if isinstance(m, AIMessage) and (m.content or "").strip():
            c = m.content
            return c if isinstance(c, str) else str(c)
    return ""
