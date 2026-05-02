"""Debate multiagente AutoGen (Gemini via endpoint OpenAI-compatível)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

_LOG = Path(__file__).resolve().parents[1] / "data" / "logs" / "debate.jsonl"


def _client():
    return OpenAIChatCompletionClient(
        model=os.environ.get("GEMINI_MODEL_EX11", os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")).replace(
            "models/", ""
        ),
        api_key=os.environ["GOOGLE_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )


def executar_debate(tema: str, rodadas: int = 4) -> dict:
    """rodadas controla quantas voltas completas (P→C→S) — desafio extra."""
    client = _client()
    pesquisador = AssistantAgent(
        "pesquisador",
        model_client=client,
        system_message="És pesquisador: propõe análise estruturada em PT-PT sobre o tema.",
    )
    critico = AssistantAgent(
        "critico",
        model_client=client,
        system_message="És crítico: aponta falhas e perguntas em aberto.",
    )
    sintetizador = AssistantAgent(
        "sintetizador",
        model_client=client,
        system_message="És sintetizador: fecha relatório breve integrando debate.",
    )
    # Cada “rodada” ≈ 3 mensagens (pesquisador, crítico, sintetizador em sequência).
    max_msgs = max(3, int(rodadas)) * 3 + 2
    team = RoundRobinGroupChat(
        [pesquisador, critico, sintetizador],
        termination_condition=MaxMessageTermination(max_messages=max_msgs),
    )

    async def _run():
        return await team.run(task=tema)

    result = asyncio.run(_run())
    msgs = getattr(result, "messages", []) or []
    linhas = []
    for m in msgs:
        src = getattr(m, "source", getattr(m, "name", "agent"))
        body = getattr(m, "content", str(m))
        linhas.append({"role": src, "content": body})
    _LOG.parent.mkdir(parents=True, exist_ok=True)
    with _LOG.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "tema": tema,
                    "rodadas_pedido": rodadas,
                    "mensagens": linhas,
                },
                ensure_ascii=False,
            )
            + "\n"
        )
    return {"log": linhas, "relatorio_final": linhas[-1]["content"] if linhas else ""}
