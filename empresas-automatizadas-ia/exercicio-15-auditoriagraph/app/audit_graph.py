"""Grafo de auditoria com ramificação por risco e relatório estruturado (extra)."""

from __future__ import annotations

import json
import os
from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph


class AuditState(TypedDict):
    achado: str
    risco: Literal["baixo", "medio", "alto", ""]
    resposta: str
    relatorio: str
    logs: list[str]


def _llm() -> ChatGoogleGenerativeAI:
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").replace("models/", "")
    return ChatGoogleGenerativeAI(model=model, temperature=0.1)


def _chat(system: str, user: str) -> str:
    llm = _llm()
    msg = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return getattr(msg, "content", str(msg)) or ""


def n_classificar(state: AuditState) -> dict:
    sys = (
        "Classifica risco do achado em PT-PT. Devolve só JSON: "
        '{"risco": "baixo"|"medio"|"alto", "justificativa_curta": str}.'
    )
    raw = _chat(sys, state["achado"])
    risco: Literal["baixo", "medio", "alto"] = "medio"
    try:
        data = json.loads(raw)
        r = str(data.get("risco", "medio")).lower()
        if r in ("baixo", "medio", "alto"):
            risco = r  # type: ignore[assignment]
        just = data.get("justificativa_curta", "")
    except json.JSONDecodeError:
        just = raw
    log = f"[classificar] risco={risco} | {just[:240]}"
    return {"risco": risco, "logs": state.get("logs", []) + [log]}


def route_risco(state: AuditState) -> str:
    r = state.get("risco") or "medio"
    if r == "baixo":
        return "baixo"
    if r == "alto":
        return "alto"
    return "medio"


def n_baixo(state: AuditState) -> dict:
    sys = "És auditor interno. Para risco baixo, dá orientação simples e acionável em PT-PT (lista curta)."
    txt = _chat(sys, state["achado"])
    rel = _relatorio(state["achado"], "baixo", txt, "Baixo impacto; monitorização rotineira.")
    return {"resposta": txt, "relatorio": rel, "logs": state.get("logs", []) + ["[baixo] resposta automática"]}


def n_medio(state: AuditState) -> dict:
    sys = "És auditor interno. Para risco médio, pede evidências adicionais específicas em PT-PT."
    txt = _chat(sys, state["achado"])
    rel = _relatorio(state["achado"], "medio", txt, "Coletar evidências antes de fechar.")
    return {"resposta": txt, "relatorio": rel, "logs": state.get("logs", []) + ["[medio] pedido de evidências"]}


def n_alto(state: AuditState) -> dict:
    sys = "És auditor interno. Para risco alto, encaminha para revisão humana com urgência e checkpoints em PT-PT."
    txt = _chat(sys, state["achado"])
    rel = _relatorio(state["achado"], "alto", txt, "Escalar para revisão humana imediata.")
    return {"resposta": txt, "relatorio": rel, "logs": state.get("logs", []) + ["[alto] revisão humana"]}


def _relatorio(achado: str, risco: str, encaminhamento: str, recomendacao: str) -> str:
    sys = (
        "Monta relatório PT-PT em JSON com chaves: risco, causa, consequencia, recomendacao, resumo_encaminhamento."
    )
    raw = _chat(
        sys,
        f"Achado:\n{achado}\nRisco classificado: {risco}\nEncaminhamento:\n{encaminhamento}\nRecomendação base: {recomendacao}",
    )
    try:
        json.loads(raw)
        return raw
    except json.JSONDecodeError:
        return json.dumps(
            {
                "risco": risco,
                "causa": "(inferir do achado)",
                "consequencia": "Potencial exposição operacional ou compliance.",
                "recomendacao": recomendacao,
                "resumo_encaminhamento": encaminhamento[:800],
            },
            ensure_ascii=False,
        )


def compilar():
    g = StateGraph(AuditState)
    g.add_node("classificar", n_classificar)
    g.add_node("baixo", n_baixo)
    g.add_node("medio", n_medio)
    g.add_node("alto", n_alto)
    g.add_edge(START, "classificar")
    g.add_conditional_edges(
        "classificar",
        route_risco,
        {"baixo": "baixo", "medio": "medio", "alto": "alto"},
    )
    g.add_edge("baixo", END)
    g.add_edge("medio", END)
    g.add_edge("alto", END)
    return g.compile()


def executar(achado: str) -> dict:
    app = compilar()
    out = app.invoke({"achado": achado.strip(), "risco": "", "resposta": "", "relatorio": "", "logs": []})
    return {
        "risco": out.get("risco"),
        "resposta": out.get("resposta"),
        "relatorio": out.get("relatorio"),
        "logs": out.get("logs") or [],
    }
