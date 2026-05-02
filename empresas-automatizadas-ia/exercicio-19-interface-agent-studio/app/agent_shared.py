"""Agente partilhado entre Streamlit e Gradio."""

from __future__ import annotations

import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI


def responder(
    mensagem: str,
    modelo: str,
    temperatura: float,
    tom: str,
) -> str:
    model = modelo.replace("models/", "")
    llm = ChatGoogleGenerativeAI(model=model, temperature=float(temperatura))
    sys = f"És assistente em PT-PT. Tom: {tom}."
    msg = llm.invoke([SystemMessage(content=sys), HumanMessage(content=mensagem)])
    return getattr(msg, "content", str(msg)) or ""
