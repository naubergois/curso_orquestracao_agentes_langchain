"""Chatbot local via Ollama + comparação opcional com Gemini (nuvem)."""

from __future__ import annotations

import os

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI


SYS = "És assistente útil em PT-PT. Respostas curtas e claras."


def _ollama():
    base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    return ChatOllama(base_url=base, model=model, temperature=0.2)


def chat_local(mensagem: str) -> str:
    llm = _ollama()
    msg = llm.invoke([SystemMessage(content=SYS), HumanMessage(content=mensagem)])
    return getattr(msg, "content", str(msg)) or ""


def chat_cloud(mensagem: str) -> str:
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").replace("models/", "")
    llm = ChatGoogleGenerativeAI(model=model, temperature=0.2)
    msg = llm.invoke([SystemMessage(content=SYS), HumanMessage(content=mensagem)])
    return getattr(msg, "content", str(msg)) or ""
