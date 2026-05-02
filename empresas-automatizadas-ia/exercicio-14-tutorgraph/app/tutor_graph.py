"""Grafo de tutoria: diagnosticar → explicar → exercitar → corrigir → revisar (ou voltar a explicar)."""

from __future__ import annotations

import json
import operator
import os
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph


def _llm() -> ChatGoogleGenerativeAI:
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").replace("models/", "")
    return ChatGoogleGenerativeAI(model=model, temperature=0.2)


class TutorState(TypedDict):
    tema: str
    nivel: str
    diagnostico: str
    explicacao: str
    exercicio: str
    resposta_aluno: str
    gabarito: str
    correto: bool
    feedback: str
    etapa: Literal["diagnosticar", "explicar", "exercitar", "corrigir", "revisar", "fim"]
    logs: Annotated[list[str], operator.add]


def _chat(system: str, user: str) -> str:
    llm = _llm()
    msg = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return getattr(msg, "content", str(msg)) or ""


def n_diagnosticar(state: TutorState) -> dict:
    tema = state["tema"]
    nivel = state.get("nivel") or "iniciante"
    sys = "És tutor. Devolve só JSON: {\"diagnostico\": str, \"nivel_sugerido\": str}."
    raw = _chat(sys, f"Tema: {tema}. Nível declarado: {nivel}.")
    try:
        data = json.loads(raw)
        diag = data.get("diagnostico", raw)
        nv = data.get("nivel_sugerido", nivel)
    except json.JSONDecodeError:
        diag, nv = raw, nivel
    log = f"[diagnosticar] {diag[:400]}"
    return {"diagnostico": diag, "nivel": nv, "etapa": "explicar", "logs": [log]}


def n_explicar(state: TutorState) -> dict:
    sys = "És tutor em PT-PT. Explica o tema de forma clara para o nível indicado (até 120 palavras)."
    txt = _chat(sys, f"Tema: {state['tema']}\nDiagnóstico: {state['diagnostico']}\nNível: {state['nivel']}")
    log = f"[explicar] {txt[:400]}"
    return {"explicacao": txt, "etapa": "exercitar", "logs": [log]}


def n_exercitar(state: TutorState) -> dict:
    sys = 'És tutor. Cria um exercício breve e devolve JSON: {"enunciado": str, "gabarito": str}.'
    raw = _chat(sys, f"Tema: {state['tema']}\nExplicação dada: {state['explicacao']}")
    try:
        data = json.loads(raw)
        enun = data.get("enunciado", raw)
        gab = data.get("gabarito", "")
    except json.JSONDecodeError:
        enun, gab = raw, ""
    log = f"[exercitar] {enun[:400]}"
    return {"exercicio": enun, "gabarito": gab, "etapa": "corrigir", "logs": [log]}


def n_corrigir(state: TutorState) -> dict:
    resposta = (state.get("resposta_aluno") or "").strip()
    gab = state.get("gabarito") or ""
    sys = "És tutor. Avalia se a resposta cobre o gabarito. Devolve só JSON: {\"correto\": bool, \"feedback\": str}."
    raw = _chat(sys, f"Enunciado: {state['exercicio']}\nGabarito: {gab}\nResposta do aluno: {resposta}")
    ok = False
    fb = raw
    try:
        data = json.loads(raw)
        ok = bool(data.get("correto", False))
        fb = data.get("feedback", fb)
    except json.JSONDecodeError:
        ok = bool(resposta and gab and resposta.lower() in gab.lower())
    log = f"[corrigir] correto={ok} | {fb[:300]}"
    return {"correto": ok, "feedback": fb, "etapa": "revisar" if ok else "explicar", "logs": [log]}


def n_revisar(state: TutorState) -> dict:
    sys = "És tutor. Fecha sessão com revisão de 3 marcadores e próximo tema sugerido (PT-PT)."
    txt = _chat(sys, f"Tema: {state['tema']}\nFeedback final: {state['feedback']}")
    log = f"[revisar] {txt[:400]}"
    return {"etapa": "fim", "logs": [log], "explicacao": state["explicacao"] + "\n\n--- Revisão ---\n" + txt}


def route_pos_corrigir(state: TutorState) -> str:
    return "revisar" if state.get("correto") else "explicar"


def compilar_grafo():
    g = StateGraph(TutorState)
    g.add_node("diagnosticar", n_diagnosticar)
    g.add_node("explicar", n_explicar)
    g.add_node("exercitar", n_exercitar)
    g.add_node("corrigir", n_corrigir)
    g.add_node("revisar", n_revisar)
    g.add_edge(START, "diagnosticar")
    g.add_edge("diagnosticar", "explicar")
    g.add_edge("explicar", "exercitar")
    g.add_edge("exercitar", "corrigir")
    g.add_conditional_edges("corrigir", route_pos_corrigir, {"revisar": "revisar", "explicar": "explicar"})
    g.add_edge("revisar", END)
    return g.compile()


def executar_sessao(tema: str, resposta_aluno: str = "", nivel: str = "iniciante") -> dict:
    app = compilar_grafo()
    init: TutorState = {
        "tema": tema,
        "nivel": nivel,
        "diagnostico": "",
        "explicacao": "",
        "exercicio": "",
        "resposta_aluno": resposta_aluno,
        "gabarito": "",
        "correto": False,
        "feedback": "",
        "etapa": "diagnosticar",
        "logs": [],
    }
    # LangGraph reduce logs - provide empty list
    out = app.invoke(init)
    # Normalizar saída para JSON-friendly
    logs = out.get("logs") or []
    return {
        "tema": out.get("tema"),
        "nivel": out.get("nivel"),
        "diagnostico": out.get("diagnostico"),
        "explicacao": out.get("explicacao"),
        "exercicio": out.get("exercicio"),
        "correto": out.get("correto"),
        "feedback": out.get("feedback"),
        "etapa_final": out.get("etapa"),
        "logs": logs,
    }
