"""Configuração do modelo de chat (Gemini via LangChain), alinhada ao curso."""

from __future__ import annotations

import os

from langchain_google_genai import ChatGoogleGenerativeAI


_DEFAULT_MODEL = "gemini-2.0-flash"


def nome_modelo() -> str:
    raw = (os.environ.get("GEMINI_MODEL") or _DEFAULT_MODEL).strip() or _DEFAULT_MODEL
    return raw.removeprefix("models/")


def criar_chat(temperature: float = 0.4) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=nome_modelo(), temperature=temperature)
