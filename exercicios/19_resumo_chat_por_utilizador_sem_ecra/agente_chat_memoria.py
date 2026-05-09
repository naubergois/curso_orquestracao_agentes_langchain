"""Agente de chat com LangGraph (MemorySaver) + contexto de resumos anteriores (PostgreSQL)."""

from __future__ import annotations

import os
from typing import Any

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from memoria_resumo_db import ler_resumo_acumulado


def _model_name() -> str:
    return (os.environ.get("GEMINI_MODEL_EX19") or os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").strip()


def _ensure_api_key() -> None:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "Defina GOOGLE_API_KEY ou GEMINI_API_KEY no `.env` na raiz do repositório."
        )
    os.environ.setdefault("GOOGLE_API_KEY", key)


def criar_llm_chat(temperature: float = 0.4) -> ChatGoogleGenerativeAI:
    _ensure_api_key()
    return ChatGoogleGenerativeAI(model=_model_name(), temperature=temperature)


def criar_llm_resumo(temperature: float = 0.2) -> ChatGoogleGenerativeAI:
    _ensure_api_key()
    return ChatGoogleGenerativeAI(model=_model_name(), temperature=temperature)


_SYSTEM_BASE = """És um assistente útil. Responde em português europeu, com clareza e concisão.
Se nas mensagens existir um bloco **«Contexto de conversas anteriores»**, trata-o como memória fiável
a menos que o utilizador o corrija explicitamente nesta sessão."""


@tool
def eco_ping(mensagem: str = "") -> str:
    """Ferramenta mínima (demo): devolve confirmação; não é necessária para o exercício."""
    return "pong" if not (mensagem or "").strip() else f"pong: {(mensagem or '')[:200]}"


def criar_grafo_chat() -> Any:
    llm = criar_llm_chat()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_BASE),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return create_react_agent(
        llm,
        tools=[eco_ping],
        prompt=prompt,
        checkpointer=MemorySaver(),
    )


def mensagens_para_texto(mensagens: list[Any]) -> str:
    linhas: list[str] = []
    for m in mensagens:
        t = getattr(m, "type", None) or m.__class__.__name__
        c = getattr(m, "content", "")
        if isinstance(c, list):
            c = str(c)
        linhas.append(f"{t}: {c}")
    return "\n".join(linhas)


def contexto_resumo_anteriores(external_id: str) -> str:
    r = ler_resumo_acumulado(external_id).strip()
    if not r:
        return "(Ainda não há resumo de conversas anteriores para este utilizador.)"
    return r


def mensagens_iniciais_sessao(external_id: str, texto_utilizador: str) -> list[Any]:
    """Primeiro turno: injeta `SystemMessage` com resumo da BD se existir; senão só a pergunta do utilizador."""
    from langchain_core.messages import HumanMessage, SystemMessage

    r = ler_resumo_acumulado(external_id).strip()
    if r:
        return [
            SystemMessage(
                content=(
                    "Contexto de conversas anteriores (persistido por resumo; pode estar incompleto):\n\n" + r
                )
            ),
            HumanMessage(content=texto_utilizador),
        ]
    return [HumanMessage(content=texto_utilizador)]


def config_thread(session_uuid: str) -> dict:
    return {"configurable": {"thread_id": session_uuid}}
