"""LangGraph: pipeline Carregar laudos → Avaliar (Pydantic) → Gravar no Postgres."""

from __future__ import annotations

import os
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

import db_laudos
from models_clinicos import AvaliacaoGravidade


class EstadoAvaliacao(TypedDict, total=False):
    paciente_id: int
    texto_laudos: str
    ficha_txt: str
    avaliacao_dict: dict[str, Any] | None
    erro: str | None


def _modelo() -> str:
    return (os.environ.get("GEMINI_MODEL_EX23") or os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").strip()


def _garantir_chave() -> None:
    k = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not k:
        raise RuntimeError("Defina GOOGLE_API_KEY ou GEMINI_API_KEY.")
    os.environ.setdefault("GOOGLE_API_KEY", k)


def no_carregar(estado: EstadoAvaliacao) -> dict[str, Any]:
    pid = int(estado["paciente_id"])
    f = db_laudos.ficha_paciente(pid)
    if not f:
        return {"erro": f"Paciente {pid} inexistente.", "texto_laudos": "", "ficha_txt": ""}
    ficha = (
        f"Nome: {f['nome_completo']}\nIdade: {f['idade']}\nSexo: {f.get('sexo')}\n"
        f"Alergias: {f.get('alergias')}\nNotas: {f.get('observacoes_clinicas')}"
    )
    txt = db_laudos.laudos_paciente_texto(pid)
    return {"texto_laudos": txt, "ficha_txt": ficha, "erro": None}


def no_avaliar(estado: EstadoAvaliacao) -> dict[str, Any]:
    if estado.get("erro"):
        return {}
    _garantir_chave()
    llm = ChatGoogleGenerativeAI(model=_modelo(), temperature=0.15)
    structured = llm.with_structured_output(AvaliacaoGravidade)
    prompt = f"""És um **médico formador** (cenário simulado). Com base **apenas** na ficha e nos laudos abaixo,
produz uma avaliação estruturada de **gravidade potencial** do conjunto laboratorial (não é diagnóstico definitivo).

FICHA:
{estado.get("ficha_txt", "")}

LAUDOS:
{estado.get("texto_laudos", "")}

Regras:
- Preenche `paciente_id` exactamente com {estado["paciente_id"]}.
- Séveridade coerente com achados (ex.: troponina em curva ascendente → pelo menos `elevada` ou `critica`).
- `hipoteses_patologicas` como hipóteses a discutir, não como conclusões fechadas.
- Português europeu, tom clínico conciso.
"""
    try:
        out = structured.invoke([HumanMessage(content=prompt)])
        if not isinstance(out, AvaliacaoGravidade):
            return {"erro": "Resposta estruturada inválida.", "avaliacao_dict": None}
        return {"avaliacao_dict": out.model_dump(mode="json"), "erro": None}
    except Exception as e:
        return {"erro": str(e), "avaliacao": None}


def no_gravar(estado: EstadoAvaliacao) -> dict[str, Any]:
    d = estado.get("avaliacao_dict")
    if estado.get("erro") or not isinstance(d, dict):
        return {}
    try:
        av = AvaliacaoGravidade.model_validate(d)
    except Exception:
        return {}
    payload = av.model_dump(mode="json")
    db_laudos.inserir_avaliacao(
        av.paciente_id,
        av.nivel.value,
        av.score_0_100,
        payload,
    )
    return {}


def construir_grafo_avaliacao():
    g = StateGraph(EstadoAvaliacao)
    g.add_node("carregar", no_carregar)
    g.add_node("avaliar", no_avaliar)
    g.add_node("gravar", no_gravar)
    g.add_edge(START, "carregar")
    g.add_edge("carregar", "avaliar")
    g.add_edge("avaliar", "gravar")
    g.add_edge("gravar", END)
    return g.compile()


def executar_avaliacao(paciente_id: int) -> EstadoAvaliacao:
    app = construir_grafo_avaliacao()
    return app.invoke({"paciente_id": int(paciente_id)})
