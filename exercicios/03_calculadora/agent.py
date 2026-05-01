"""Exercício 03 — agente com ferramenta calculadora (LangGraph + Gemini).

A ferramenta `calculadora` avalia expressões numéricas de forma restrita (+, -, *, /, **,
parêntesis, números). O grafo ReAct (`create_react_agent`) decide quando chamar a tool.
"""

from __future__ import annotations

import ast
import operator
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _avaliar_ast(no: ast.AST) -> float:
    if isinstance(no, ast.Expression):
        return _avaliar_ast(no.body)
    if isinstance(no, ast.Constant):
        if isinstance(no.value, (int, float)) and not isinstance(no.value, bool):
            return float(no.value)
        raise ValueError("Só são permitidos números.")
    if isinstance(no, ast.BinOp):
        op = _OPS.get(type(no.op))
        if op is None:
            raise ValueError("Operador não permitido.")
        return float(op(_avaliar_ast(no.left), _avaliar_ast(no.right)))
    if isinstance(no, ast.UnaryOp):
        op = _OPS.get(type(no.op))
        if op is None:
            raise ValueError("Operador unário não permitido.")
        return float(op(_avaliar_ast(no.operand)))
    raise ValueError("Expressão não suportada.")


def _calcular_seguro(expressao: str) -> float:
    arvore = ast.parse(expressao.strip(), mode="eval")
    return _avaliar_ast(arvore)


@tool
def calculadora(expressao: str) -> str:
    """Avalia uma expressão matemática com +, -, *, /, ** e parêntesis (apenas números).

    Exemplos: "2 + 2", "(10 + 5) / 3", "2 ** 8"
    """
    try:
        valor = _calcular_seguro(expressao)
        # Formato limpo: inteiro se for inteiro
        if valor == int(valor):
            return str(int(valor))
        return str(round(valor, 10))
    except Exception as e:
        return f"Erro ao calcular: {e}"


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_local_env()

_DEFAULT_GEMINI = "gemini-2.0-flash"


def _ensure_api_key() -> None:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "Defina GOOGLE_API_KEY ou GEMINI_API_KEY no `.env` na raiz do repositório."
        )
    os.environ.setdefault("GOOGLE_API_KEY", key)


def _modelo() -> str:
    nome = (os.environ.get("GEMINI_MODEL") or _DEFAULT_GEMINI).strip() or _DEFAULT_GEMINI
    base = nome.removeprefix("models/")
    if base.startswith("gemini-1.5"):
        print(
            "Aviso: modelos `gemini-1.5*` não são usados neste curso → "
            f"`{_DEFAULT_GEMINI}`. Atualize GEMINI_MODEL no `.env`.",
            file=sys.stderr,
        )
        return _DEFAULT_GEMINI
    return nome


def build_chat_model() -> ChatGoogleGenerativeAI:
    _ensure_api_key()
    return ChatGoogleGenerativeAI(model=_modelo(), temperature=0.2)


def build_graph():
    """Grafo ReAct com memória em RAM (o `thread_id` no Streamlit separa conversas)."""
    return create_react_agent(
        build_chat_model(),
        tools=[calculadora],
        checkpointer=MemorySaver(),
    )


def _eh_429(exc: BaseException) -> bool:
    t = str(exc).upper()
    return "429" in t or "RESOURCE_EXHAUSTED" in t


def proxima_mensagem_utilizador(
    graph,
    mensagem: str,
    thread_id: str,
) -> None:
    """Acrescenta uma mensagem humana ao thread e corre o agente até resposta final."""
    config = {"configurable": {"thread_id": thread_id}}
    max_t = max(1, int(os.environ.get("GEMINI_RETRY_ATTEMPTS", "5")))
    base = max(0.5, float(os.environ.get("GEMINI_RETRY_DELAY_SEC", "2")))
    ultimo: BaseException | None = None

    for tentativa in range(max_t):
        try:
            graph.invoke({"messages": [HumanMessage(content=mensagem)]}, config)
            return
        except Exception as e:
            ultimo = e
            if _eh_429(e) and tentativa < max_t - 1:
                time.sleep(min(base * (2**tentativa), 60.0))
                continue
            break

    assert ultimo is not None
    if _eh_429(ultimo):
        raise RuntimeError(
            "API Gemini (429). Espere ou ajuste GEMINI_MODEL no `.env`. "
            f"Modelo: `{_modelo()}`."
        ) from ultimo
    raise ultimo


def obter_mensagens_do_thread(graph, thread_id: str):
    """Lista de mensagens LangChain do estado actual do thread."""
    config = {"configurable": {"thread_id": thread_id}}
    snap = graph.get_state(config)
    if not snap or not snap.values:
        return []
    return list(snap.values.get("messages") or [])


def texto_para_mostrar(msg) -> str | None:
    if isinstance(msg, HumanMessage):
        c = msg.content
        return c if isinstance(c, str) else str(c)
    if isinstance(msg, AIMessage):
        parts: list[str] = []
        if getattr(msg, "tool_calls", None):
            nomes = [tc.get("name", "?") for tc in msg.tool_calls]
            parts.append(f"*(ferramentas: {', '.join(nomes)})*")
        c = msg.content
        if c:
            parts.append(c if isinstance(c, str) else str(c))
        return "\n\n".join(parts) if parts else None
    if isinstance(msg, ToolMessage):
        return f"🔧 `{msg.name}` → {msg.content}"
    return None
