"""LangGraph: classificação → contexto RAG → especialista → revisor → relatório."""

from __future__ import annotations

import json
import operator
import os
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

from app.rag_store import formatar_contexto


class Estado(TypedDict):
    mensagem: str
    classe_demanda: str
    contexto: str
    especialista: str
    revisor: str
    relatorio: str
    avaliacao_auto: str
    logs: Annotated[list[str], operator.add]


def _llm(t: float = 0.2) -> ChatGoogleGenerativeAI:
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").replace("models/", "")
    return ChatGoogleGenerativeAI(model=model, temperature=t)


def _chat(system: str, user: str, t: float = 0.2) -> str:
    llm = _llm(t)
    msg = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return getattr(msg, "content", str(msg)) or ""


def n_classificar(state: Estado) -> dict:
    sys = 'Classifica a mensagem do cliente. Devolve só JSON {"classe": one of [suporte,faturacao,legal,outro]}.'
    raw = _chat(sys, state["mensagem"], t=0.1)
    try:
        data = json.loads(raw)
        cls = str(data.get("classe", "outro"))
    except json.JSONDecodeError:
        cls = "outro"
    return {"classe_demanda": cls, "logs": [f"[classificar] {cls}"]}


def n_rag(state: Estado) -> dict:
    ctx = formatar_contexto(state["mensagem"], k=4)
    return {"contexto": ctx, "logs": ["[rag] contexto montado"]}


def n_especialista(state: Estado) -> dict:
    sys = (
        "És especialista interno. Usa o contexto dos documentos quando útil. "
        "Responde em PT-PT com passos claros. Se faltar informação, diz o que falta."
    )
    user = f"Mensagem:\n{state['mensagem']}\n\nContexto:\n{state['contexto']}"
    out = _chat(sys, user, t=0.3)
    return {"especialista": out, "logs": ["[especialista] resposta gerada"]}


def n_revisor(state: Estado) -> dict:
    sys = "És revisor: verifica consistência, riscos e linguagem. Produz versão melhorada em PT-PT."
    user = f"Classe: {state['classe_demanda']}\nRascunho:\n{state['especialista']}"
    out = _chat(sys, user, t=0.2)
    return {"revisor": out, "logs": ["[revisor] revisão concluída"]}


def n_relatorio(state: Estado) -> dict:
    sys = "Gera relatório final conciso com: resumo, decisão recomendada, avisos."
    user = (
        f"Cliente disse:\n{state['mensagem']}\n\n"
        f"Classe: {state['classe_demanda']}\n\n"
        f"Resposta revisada:\n{state['revisor']}\n\n"
        f"Fontes usadas:\n{state['contexto'][:1200]}"
    )
    out = _chat(sys, user, t=0.2)
    return {"relatorio": out, "logs": ["[relatorio] entregue"]}


def n_avaliar(state: Estado) -> dict:
    sys = 'Avalia a resposta revisada. Devolve JSON {"nota":1-5,"motivo":str}.'
    raw = _chat(sys, f"Pergunta:\n{state['mensagem']}\n\nResposta:\n{state['revisor']}", t=0.0)
    return {"avaliacao_auto": raw, "logs": ["[avaliacao] rubrica LLM"]}


def compilar():
    g = StateGraph(Estado)
    for nome, fn in [
        ("classificar", n_classificar),
        ("rag", n_rag),
        ("especialista", n_especialista),
        ("revisor", n_revisor),
        ("relatorio", n_relatorio),
        ("avaliar", n_avaliar),
    ]:
        g.add_node(nome, fn)
    g.add_edge(START, "classificar")
    g.add_edge("classificar", "rag")
    g.add_edge("rag", "especialista")
    g.add_edge("especialista", "revisor")
    g.add_edge("revisor", "relatorio")
    g.add_edge("relatorio", "avaliar")
    g.add_edge("avaliar", END)
    return g.compile()


def executar_pipeline(mensagem: str) -> dict:
    app = compilar()
    init: Estado = {
        "mensagem": mensagem.strip(),
        "classe_demanda": "",
        "contexto": "",
        "especialista": "",
        "revisor": "",
        "relatorio": "",
        "avaliacao_auto": "",
        "logs": [],
    }
    out = app.invoke(init)
    return {
        "classe_demanda": out.get("classe_demanda"),
        "resposta_cliente": out.get("revisor"),
        "relatorio_interno": out.get("relatorio"),
        "avaliacao_automatica": out.get("avaliacao_auto"),
        "logs": out.get("logs") or [],
    }
