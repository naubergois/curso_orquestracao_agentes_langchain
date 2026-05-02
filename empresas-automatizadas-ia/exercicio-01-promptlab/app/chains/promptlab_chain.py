"""Chain simples: SystemMessage + HumanMessage → AIMessage."""

from __future__ import annotations

import os
import time

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.schemas.pergunta import PerfilAssistente
from app.services.llm_factory import criar_chat
from app.services.prompts import obter_system_prompt


def _eh_quota(exc: BaseException) -> bool:
    t = str(exc).upper()
    return "429" in t or "RESOURCE_EXHAUSTED" in t


def gerar_resposta(perfil: PerfilAssistente, pergunta: str) -> str:
    llm = criar_chat()
    mensagens = [
        SystemMessage(content=obter_system_prompt(perfil)),
        HumanMessage(content=pergunta),
    ]
    max_t = max(1, int(os.environ.get("GEMINI_RETRY_ATTEMPTS", "5")))
    base = max(0.5, float(os.environ.get("GEMINI_RETRY_DELAY_SEC", "2")))
    ultimo: BaseException | None = None

    for tentativa in range(max_t):
        try:
            res: AIMessage = llm.invoke(mensagens)
            if isinstance(res.content, str):
                return res.content.strip()
            return str(res.content).strip()
        except Exception as e:
            ultimo = e
            if _eh_quota(e) and tentativa < max_t - 1:
                time.sleep(min(base * (2**tentativa), 60.0))
                continue
            raise

    assert ultimo is not None
    raise ultimo
