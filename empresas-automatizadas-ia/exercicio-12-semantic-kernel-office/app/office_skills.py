"""Skills de escritório usando Semantic Kernel + cliente OpenAI-compatível (Gemini)."""

from __future__ import annotations

import json
import os
from enum import Enum

from openai import AsyncOpenAI
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory


class SkillNome(str, Enum):
    resumir = "resumir"
    email = "email"
    tarefas = "tarefas"
    reuniao = "reuniao"


def _chat_service() -> OpenAIChatCompletion:
    model = os.environ.get("GEMINI_MODEL_SK", os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")).replace(
        "models/", ""
    )
    client = AsyncOpenAI(
        api_key=os.environ["GOOGLE_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    return OpenAIChatCompletion(ai_model_id=model, async_client=client)


async def _gerar(service: OpenAIChatCompletion, system: str, user: str) -> str:
    hist = ChatHistory(system_message=system)
    hist.add_user_message(user)
    settings = OpenAIChatPromptExecutionSettings()
    parts = await service.get_chat_message_contents(hist, settings)
    if not parts:
        return ""
    last = parts[-1]
    return getattr(last, "content", str(last)) or ""


_SYS_RESUMIR = """És assistente administrativo. Resume o texto em PT-PT com marcadores curtos.
Mantém factos e datas; remove redundância."""


_SYS_EMAIL = """És assistente administrativo. Redige um e-mail profissional em PT-PT com assunto sugerido no topo na linha 'Assunto: ...'.
Tom cordial e objetivo. Corpo com saudação e encerramento."""


_SYS_TAREFAS = """És assistente administrativo. Transforma o texto numa lista numerada de tarefas acionáveis em PT-PT.
Cada linha: verbo no imperativo + resultado esperável."""


_SYS_REUNIAO = """Primeiro resume a ata/reunião; depois redige e-mail de encaminhamento curto com próximos passos.
Responde em JSON com chaves: resumo (string), assunto_email (string), corpo_email (string)."""


async def executar_skill(nome: SkillNome, texto: str) -> dict:
    svc = _chat_service()
    texto = texto.strip()
    if nome == SkillNome.resumir:
        out = await _gerar(svc, _SYS_RESUMIR, texto)
        return {"skill": nome.value, "resultado": out}
    if nome == SkillNome.email:
        out = await _gerar(svc, _SYS_EMAIL, texto)
        return {"skill": nome.value, "resultado": out}
    if nome == SkillNome.tarefas:
        out = await _gerar(svc, _SYS_TAREFAS, texto)
        return {"skill": nome.value, "resultado": out}
    raw = await _gerar(svc, _SYS_REUNIAO, texto)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"resumo": raw, "assunto_email": "(extrair manualmente)", "corpo_email": raw}
    return {"skill": nome.value, "resultado": data}
