"""Agente ReAct (LangGraph) para médicos: SQL (Postgres) + RAG (Chroma)."""

from __future__ import annotations

import json
import os
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

import db_laudos

_retriever: Any | None = None


def configurar_rag(retriever: Any | None) -> None:
    global _retriever
    _retriever = retriever


def _modelo() -> str:
    return (os.environ.get("GEMINI_MODEL_EX23") or os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").strip()


def _garantir_chave() -> None:
    k = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not k:
        raise RuntimeError("Defina GOOGLE_API_KEY ou GEMINI_API_KEY.")
    os.environ.setdefault("GOOGLE_API_KEY", k)


@tool
def listar_pacientes_demo() -> str:
    """Lista os 10 pacientes fictícios com id, nome, idade e último nível de gravidade avaliado (se existir)."""
    rows = db_laudos.listar_pacientes_resumo()
    return json.dumps(rows, ensure_ascii=False, indent=2, default=str)


@tool
def obter_ficha_clinica_resumo(paciente_id: int) -> str:
    """Devolve ficha demográfica e notas clínicas do paciente (Postgres)."""
    f = db_laudos.ficha_paciente(int(paciente_id))
    if not f:
        return f"(paciente_id={paciente_id} não encontrado)"
    return json.dumps(dict(f), ensure_ascii=False, indent=2, default=str)


@tool
def obter_texto_laudos_laboratoriais(paciente_id: int) -> str:
    """Concatena todos os laudos laboratoriais do paciente tal como estão na base (texto bruto)."""
    return db_laudos.laudos_paciente_texto(int(paciente_id))


@tool
def obter_ultima_avaliacao_gravidade_json(paciente_id: int) -> str:
    """Última linha da tabela `avaliacoes_engine` para o paciente (JSON), incluindo payload Pydantic serializado."""
    row = db_laudos.ultima_avaliacao_dict(int(paciente_id))
    if not row:
        return "(sem avaliação gravada — pode sugerir correr o motor LangGraph na interface.)"
    return json.dumps(row, ensure_ascii=False, indent=2, default=str)


@tool
def consultar_base_pedagogica_rag(pergunta: str) -> str:
    """Recupera trechos da base Chroma (protocolos fictícios + laudos indexados). Use perguntas curtas e específicas."""
    q = (pergunta or "").strip()
    if not q:
        return "(pergunta vazia)"
    if _retriever is None:
        return "(RAG indisponível: índice Chroma não configurado.)"
    docs = _retriever.invoke(q)
    partes: list[str] = []
    for i, d in enumerate(docs, 1):
        meta = d.metadata or {}
        partes.append(f"--- Trecho {i} [meta: {meta}]\n{d.page_content}")
    return "\n\n".join(partes)[:24000]


_SYSTEM = """És um **assistente clínico de formação** para médicos, sobre **dados 100% fictícios** desta demo.

Capacidades (ferramentas):
- Listar pacientes e ler fichas/laudos na **PostgreSQL**.
- Ler a **última avaliação de gravidade** já calculada pelo motor LangGraph (Pydantic).
- Consultar a **ChromaDB** com textos pedagógicos e laudos indexados (RAG).

Regras:
- Não inventes resultados laboratoriais: se precisares, chama `obter_texto_laudos_laboratoriais`.
- Deixa explícito quando estás a inferir vs. a citar a base.
- Quando discutires patologias possíveis, usa linguagem de **hipótese diagnóstica** e cita riscos de subdiagnóstico/sobrediagnóstico.
- Português europeu. Lembra o utilizador de que isto **não** substitui parecer médico nem prática real."""


def criar_agente_chat_medico() -> Any:
    _garantir_chave()
    llm = ChatGoogleGenerativeAI(model=_modelo(), temperature=0.2)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    tools = [
        listar_pacientes_demo,
        obter_ficha_clinica_resumo,
        obter_texto_laudos_laboratoriais,
        obter_ultima_avaliacao_gravidade_json,
        consultar_base_pedagogica_rag,
    ]
    return create_react_agent(llm, tools=tools, prompt=prompt, checkpointer=MemorySaver())


def config_chat(paciente_id: int, *, thread_suffix: int = 0) -> dict:
    return {"configurable": {"thread_id": f"ex23-paciente-{int(paciente_id)}-{int(thread_suffix)}"}}


def ultima_resposta_assistente(resultado: dict) -> str:
    msgs = resultado.get("messages") or []
    for m in reversed(msgs):
        if isinstance(m, AIMessage) and (m.content or "").strip():
            c = m.content
            return c if isinstance(c, str) else str(c)
    return ""


def invocar_mensagem(graph: Any, paciente_id: int, mensagem: str, *, thread_suffix: int = 0) -> str:
    cfg = config_chat(paciente_id, thread_suffix=thread_suffix)
    out = graph.invoke({"messages": [HumanMessage(content=mensagem)]}, cfg)
    return ultima_resposta_assistente(out)
