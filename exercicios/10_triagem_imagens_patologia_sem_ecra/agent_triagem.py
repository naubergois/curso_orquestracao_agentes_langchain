"""Agente ReAct (LangGraph) para **triagem**: classifica lesões DermaMNIST, grava no MongoDB e consulta prioridades.

Ferramentas expostas ao LLM para orquestrar o fluxo sem código manual repetitivo.
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

from classificador import prever_de_vector, vetor_de_amostra_medmnist
from mongo_store import (
    contar_pendentes,
    inserir_caso,
    listar_top_prioridade,
    marcar_atendido,
    obter_caso,
)
from triagem import CLASSES_DERMA_MNIST, calcular_prioridade, nome_patologia_prioritaria


def _load_env() -> None:
    here = Path(__file__).resolve()
    for d in (here.parent, *here.parents):
        env = d / ".env"
        if env.is_file():
            load_dotenv(env, override=False)
            return


def _ensure_key() -> None:
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        raise RuntimeError("Defina GOOGLE_API_KEY ou GEMINI_API_KEY.")


@tool
def processar_amostra_derma(split: str, indice: int) -> str:
    """Extrai uma imagem DermaMNIST (28×28), classifica e regista o caso no MongoDB com prioridade.

    Args:
        split: `train`, `val` ou `test`.
        indice: posição no subconjunto MedMNIST.
    """
    split = split.strip().lower()
    if split not in ("train", "val", "test"):
        return "Erro: `split` deve ser train, val ou test."
    try:
        x, y_verd = vetor_de_amostra_medmnist(split, int(indice))
    except Exception as e:
        return f"Erro ao ler amostra: {e}"
    res = prever_de_vector(x)
    prio = calcular_prioridade(res["probabilidades"], res["classe_predita"])
    cid = f"dmnist_{split}_{int(indice)}"
    inserir_caso(
        caso_id=cid,
        origem="dermamnist",
        indice_amostra=int(indice),
        split=split,
        rotulo_verdadeiro=int(y_verd),
        resultado_classificador=res,
        prioridade=prio,
    )
    rotulo_v = CLASSES_DERMA_MNIST[y_verd] if 0 <= y_verd < len(CLASSES_DERMA_MNIST) else str(y_verd)
    return (
        f"Caso `{cid}` gravado. Predito: {res['rotulo_predito']} (conf. max {res['confianca_maxima']:.3f}). "
        f"Rótulo dataset: {rotulo_v}. Prioridade {prio}/100."
    )


@tool
def consultar_fila_prioridade(limite: int = 8) -> str:
    """Lista os casos pendentes com maior prioridade (limite predefinido 8)."""
    rows = listar_top_prioridade(max(1, min(25, int(limite))))
    if not rows:
        return "Não há casos pendentes na fila."
    linhas = []
    for i, r in enumerate(rows, 1):
        linhas.append(
            f"{i}. {r.get('caso_id')} — prioridade {r.get('prioridade')} — "
            f"pred: {r.get('rotulo_predito')} — conf {r.get('confianca_maxima', 0):.3f}"
        )
    return "\n".join(linhas)


@tool
def detalhe_caso(caso_id: str) -> str:
    """Devolve campos principais de um caso (MongoDB) pelo `caso_id`."""
    doc = obter_caso(caso_id.strip())
    if not doc:
        return f"Caso `{caso_id}` não encontrado."
    prob = list(doc.get("probabilidades") or [])
    slim = {k: v for k, v in doc.items() if k not in ("_id", "probabilidades")}
    return f"{slim}\nprobabilidades (primeiros 3): {prob[:3]}"


@tool
def finalizar_atendimento(caso_id: str) -> str:
    """Marca o caso como atendido na base de dados."""
    ok = marcar_atendido(caso_id.strip())
    return "Estado atualizado para atendido." if ok else f"Nenhuma alteração para `{caso_id}`."


@tool
def contagem_fila_pendente() -> str:
    """Número de casos ainda pendentes de atendimento."""
    n = contar_pendentes()
    alvo = nome_patologia_prioritaria()
    return f"Pendentes: {n}. Patologia com peso extra na prioridade: {alvo}."


def build_graph():
    _load_env()
    _ensure_key()
    ex = Path(__file__).resolve().parent.parent
    if str(ex) not in sys.path:
        sys.path.insert(0, str(ex))
    from lib_llm_fallback import gemini_model_candidates, make_gemini_chat_with_runtime_fallback

    prim = (
        os.environ.get("GEMINI_MODEL_EX10")
        or os.environ.get("GEMINI_MODEL")
        or "gemini-2.0-flash"
    ).strip()
    candidatos = gemini_model_candidates(primary=prim)
    llm = make_gemini_chat_with_runtime_fallback(candidatos, temperature=0.15)
    return create_react_agent(
        llm,
        tools=[
            processar_amostra_derma,
            consultar_fila_prioridade,
            detalhe_caso,
            finalizar_atendimento,
            contagem_fila_pendente,
        ],
        checkpointer=MemorySaver(),
    )


def convidar_triagem(
    mensagem_utilizador: str,
    *,
    thread_id: str = "ex10-triagem",
) -> str:
    """Uma volta de conversa com o agente (útil em scripts / testes)."""
    g = build_graph()
    out = g.invoke(
        {"messages": [HumanMessage(content=mensagem_utilizador)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    msgs = out.get("messages") or []
    if not msgs:
        return ""
    last = msgs[-1]
    c = getattr(last, "content", None)
    return c if isinstance(c, str) else str(c)
