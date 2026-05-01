"""Lógica do agente: Gemini + LangGraph (sem dependência de Streamlit)."""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent


def _load_local_env() -> None:
    """Carrega o primeiro `.env` encontrado a partir deste ficheiro até à raiz do repo."""
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_local_env()


@tool
def cumprimentar(nome: str) -> str:
    """Cumprimenta uma pessoa pelo nome. Use quando o usuário pedir um olá ou apresentação."""
    return f"Olá, {nome}! Prazer em te conhecer."


def build_agent():
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Defina GOOGLE_API_KEY ou GEMINI_API_KEY (obtenha em https://aistudio.google.com/apikey)."
        )
    os.environ.setdefault("GOOGLE_API_KEY", api_key)

    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.2,
    )
    return create_react_agent(model, tools=[cumprimentar])


def run_agent_turn(messages: list[BaseMessage]) -> tuple[list[BaseMessage], str]:
    """Executa um passo completo do grafo e devolve o histórico atualizado + texto final ao utilizador."""
    agent = build_agent()
    result = agent.invoke({"messages": messages})
    new_messages = list(result["messages"])
    final_ai = next(
        (
            m
            for m in reversed(result["messages"])
            if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None)
        ),
        None,
    )
    reply = (
        (final_ai.content if isinstance(final_ai.content, str) else str(final_ai.content))
        if final_ai
        else "(sem resposta textual)"
    )
    return new_messages, reply


def append_user_message(messages: list[BaseMessage], text: str) -> list[BaseMessage]:
    """Adiciona a mensagem do utilizador ao histórico (cópia nova da lista)."""
    return [*messages, HumanMessage(content=text)]
