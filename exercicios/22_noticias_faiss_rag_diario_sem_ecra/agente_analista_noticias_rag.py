"""Agente ReAct: conversa sobre notícias indexadas (RAG sobre FAISS)."""

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

from faiss_noticias import carregar_faiss


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
def consultar_indice_noticias_faiss(pergunta_recuperacao: str) -> str:
    """Recupera trechos do índice FAISS (semântica). Formule uma pergunta curta ou palavras-chave alinhadas com o que procura (ex.: «impacto taxas juros», «eleições autárquicas»)."""
    q = (pergunta_recuperacao or "").strip()
    if not q:
        return "(pergunta vazia)"
    vs = carregar_faiss()
    docs = vs.similarity_search(q, k=8)
    blocos: list[str] = []
    for i, d in enumerate(docs, 1):
        meta = d.metadata or {}
        cab = f"--- Trecho {i} (consulta original da recolha: {meta.get('consulta', 'n/d')})\n"
        blocos.append(cab + (d.page_content or "").strip())
    texto = "\n\n".join(blocos)
    return texto[:28000]


_SYSTEM = """És um **analista editorial** que comenta **apenas** o que constar dos trechos devolvidos pela ferramenta `consultar_indice_noticias_faiss`.

Antes de conclusões ou «leituras do dia», **invoca a ferramenta** com sub-perguntas diferentes se precisares de mais contexto (economia, política externa, sociedade, etc.).

Regras:
- Cita lacunas: o índice pode ser incompleto ou desactualizado em relação à hora actual.
- Destaca **implicações** e **riscos** em linguagem clara (português europeu), sem sensacionalismo.
- Se o utilizador pedir factos que não apareçam nos trechos, diz explicitamente que o índice não contém essa informação.
- Opcionalmente termina com **3 perguntas de seguimento** úteis para aprofundar (ainda dentro do RAG)."""


def criar_grafo_agente_analista() -> Any:
    _garantir_chave_api()
    llm = ChatGoogleGenerativeAI(model=_modelo(), temperature=0.35)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return create_react_agent(
        llm,
        tools=[consultar_indice_noticias_faiss],
        prompt=prompt,
        checkpointer=MemorySaver(),
    )


def config_analista(thread_id: str = "ex22-analista-rag") -> dict:
    return {"configurable": {"thread_id": thread_id}}


def ultima_resposta_assistente(resultado: dict) -> str:
    msgs = resultado.get("messages") or []
    for m in reversed(msgs):
        if isinstance(m, AIMessage) and (m.content or "").strip():
            c = m.content
            return c if isinstance(c, str) else str(c)
    return ""
