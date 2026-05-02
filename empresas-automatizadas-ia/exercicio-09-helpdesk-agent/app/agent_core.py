"""Agente HelpDesk com 4 ferramentas + registo JSONL."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

_LOG = Path(__file__).resolve().parents[1] / "data" / "logs" / "agent_calls.jsonl"
_TICKETS: dict[str, dict] = {}


def _log(tool_name: str, payload: dict) -> None:
    _LOG.parent.mkdir(parents=True, exist_ok=True)
    line = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        **payload,
    }
    with _LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def _model_name() -> str:
    return (
        os.environ.get("GEMINI_MODEL_EX09")
        or os.environ.get("GEMINI_MODEL")
        or "gemini-2.0-flash"
    ).replace("models/", "")


@tool
def abrir_chamado(resumo: str, area: str) -> str:
    """Abre chamado interno. area: rede | software | conta | hardware."""
    tid = f"HD-{uuid.uuid4().hex[:8].upper()}"
    _TICKETS[tid] = {"resumo": resumo, "area": area, "estado": "aberto"}
    _log("abrir_chamado", {"ticket": tid, "resumo": resumo, "area": area})
    return f"Chamado {tid} criado na área '{area}'."


@tool
def consultar_status(identificador: str) -> str:
    """Consulta estado de um chamado pelo ID (ex.: HD-ABC12345)."""
    t = _TICKETS.get(identificador.strip())
    _log("consultar_status", {"identificador": identificador, "encontrado": bool(t)})
    if not t:
        return "Chamado não encontrado."
    return f"{identificador}: estado={t['estado']}, área={t['area']}, resumo={t['resumo'][:120]}"


@tool
def classificar_problema(descricao: str) -> str:
    """Classifica o tipo técnico provável (password | rede | aplicação | hardware | indeterminado)."""
    d = descricao.lower()
    if any(w in d for w in ("senha", "palavra-passe", "password", "login", "credencial")):
        cat = "password"
    elif any(w in d for w in ("rede", "wifi", "internet", "vpn", "liga")):
        cat = "rede"
    elif any(w in d for w in ("aplicação", "app", "software", "erro", "crash")):
        cat = "aplicação"
    elif any(w in d for w in ("ecrã", "hardware", "usb", "arranque")):
        cat = "hardware"
    else:
        cat = "indeterminado"
    _log("classificar_problema", {"descricao": descricao[:200], "categoria": cat})
    return cat


@tool
def estimar_prioridade(descricao: str) -> str:
    """Estima prioridade do chamado: critica | alta | media | baixa."""
    d = descricao.lower()
    if any(w in d for w in ("parado", "todos", "email fora", "servidor", "produção")):
        pr = "critica"
    elif any(w in d for w in ("não funciona", "urgente", "deadline")):
        pr = "alta"
    elif any(w in d for w in ("lento", "às vezes")):
        pr = "media"
    else:
        pr = "baixa"
    _log("estimar_prioridade", {"prioridade": pr})
    return pr


_SYS = """És agente de helpdesk interno (PT-PT). Sê breve.
Usa ferramentas para classificar, estimar prioridade, abrir chamado ou consultar estado.
Se o utilizador descrever problema sem ID, classifica e sugere abrir chamado com área adequada."""


def build_graph():
    llm = ChatGoogleGenerativeAI(model=_model_name(), temperature=0.2)
    return create_react_agent(
        llm,
        tools=[
            abrir_chamado,
            consultar_status,
            classificar_problema,
            estimar_prioridade,
        ],
        prompt=SystemMessage(content=_SYS),
        checkpointer=MemorySaver(),
    )


def chat_turn(mensagem: str, thread_id: str) -> str:
    g = build_graph()
    out = g.invoke(
        {"messages": [HumanMessage(content=mensagem)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    last = out["messages"][-1]
    if isinstance(last, AIMessage):
        return str(last.content)
    return str(last)
