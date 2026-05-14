"""Agente ReAct (LangGraph + Gemini) — campanhas de marketing para o produto mais vendido."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from dados_vendas_demo import (
    contexto_marca_json,
    ficha_produto_json,
    produto_mais_vendido_por_unidades,
    ranking_por_unidades,
)


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_local_env()


def _modelo() -> str:
    return (os.environ.get("GEMINI_MODEL_EX21") or os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").strip()


def _garantir_chave_api() -> None:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "Defina GOOGLE_API_KEY ou GEMINI_API_KEY no `.env` na raiz do repositório."
        )
    os.environ.setdefault("GOOGLE_API_KEY", key)


@tool
def obter_ranking_vendas_json(limite: int = 8) -> str:
    """Ranking de produtos por **unidades vendidas** no período demo (JSON). Use primeiro para ver o líder."""
    limite = max(1, min(int(limite), 20))
    return json.dumps(ranking_por_unidades(limite), ensure_ascii=False, indent=2)


@tool
def obter_produto_mais_vendido_json() -> str:
    """Resumo do **produto #1 em unidades** com SKU, nome, categoria, totais de vendas e *pitch* do catálogo."""
    return json.dumps(produto_mais_vendido_por_unidades(), ensure_ascii=False, indent=2)


@tool
def obter_ficha_produto_por_sku(sku: str) -> str:
    """Ficha completa de um SKU (vendas agregadas + dados de catálogo). O argumento deve ser o SKU em maiúsculas (ex.: CAFE500)."""
    return ficha_produto_json(sku)


@tool
def obter_contexto_marca_e_canais_json() -> str:
    """Tom de voz da marca fictícia, canais sugeridos e duração típica de campanha (JSON)."""
    return contexto_marca_json()


_SYSTEM = """És **director de marketing** de retalho alimentar na rede fictícia descrita nas ferramentas.

Missão: desenhar **campanhas** centradas no **produto mais vendido em unidades** (produto estrela do período), com base **exclusiva** nos dados devolvidos pelas *tools*. Não inventes SKUs, quantidades nem euros que não apareçam no JSON.

Fluxo recomendado:
1. Consulta o ranking e/ou o resumo do produto #1.
2. Abre a ficha desse SKU para detalhe e mensagens.
3. Lê o contexto de marca/canais.

Na resposta final (português europeu), entrega:
- **Nome da campanha** (criativo, adequado à marca).
- **Público-alvo** e **proposta de valor** em 2–4 frases.
- **Pilares de mensagem** (3 bullets).
- **Canais e tácticas** (tabela ou lista): o que fazer em cada canal sugerido.
- **Calendário** sugerido (4 semanas, marcos por semana).
- **KPIs** mensuráveis (ex.: uplift de unidades, taxa de abertura email, alcance social — adapta ao canal).

Se o utilizador pedir variações (ex.: segunda campanha para o 2.º produto), volta a usar as ferramentas antes de responder."""


def criar_grafo_agente_marketing() -> Any:
    _garantir_chave_api()
    llm = ChatGoogleGenerativeAI(model=_modelo(), temperature=0.35)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    tools = [
        obter_ranking_vendas_json,
        obter_produto_mais_vendido_json,
        obter_ficha_produto_por_sku,
        obter_contexto_marca_e_canais_json,
    ]
    return create_react_agent(llm, tools=tools, prompt=prompt, checkpointer=MemorySaver())


def config_marketing(thread_id: str = "ex21-marketing-estrela") -> dict:
    return {"configurable": {"thread_id": thread_id}}


def ultima_resposta_assistente(resultado: dict) -> str:
    msgs = resultado.get("messages") or []
    for m in reversed(msgs):
        if isinstance(m, AIMessage) and (m.content or "").strip():
            c = m.content
            return c if isinstance(c, str) else str(c)
    return ""
