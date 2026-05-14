"""Agente ReAct (LangGraph + Gemini) para análise integrada de stock e vendas do mercantil."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from mercantil_paralelo import Mercantil, relatorio_estoque, relatorio_lucro_vendas


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_local_env()


def _modelo() -> str:
    return (os.environ.get("GEMINI_MODEL_EX20") or os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").strip()


def _garantir_chave_api() -> None:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "Defina GOOGLE_API_KEY ou GEMINI_API_KEY no `.env` na raiz do repositório para usar o agente."
        )
    os.environ.setdefault("GOOGLE_API_KEY", key)


def criar_ferramentas_mercantil(loja: Mercantil) -> list[Any]:
    """Tools fecham sobre a mesma instância `Mercantil` (dados alinhados aos relatórios Pydantic)."""

    @tool
    def obter_relatorio_estoque_json() -> str:
        """Relatório de **stock** actual (JSON): por SKU quantidade, preço de compra de referência, valor em stock e total."""
        snap = loja.criar_snapshot()
        return relatorio_estoque(snap).model_dump_json(indent=2, ensure_ascii=False)

    @tool
    def obter_relatorio_vendas_lucro_json() -> str:
        """Relatório de **vendas e lucro** (JSON): linhas por nota, receita, CMV, margem por linha, totais e lucro bruto."""
        snap = loja.criar_snapshot()
        return relatorio_lucro_vendas(snap).model_dump_json(indent=2, ensure_ascii=False)

    @tool
    def obter_indicadores_consolidados_json() -> str:
        """Resumo numérico único (JSON): valor total em stock, receita total, CMV total, lucro bruto, nº de linhas de venda."""
        snap = loja.criar_snapshot()
        e = relatorio_estoque(snap)
        v = relatorio_lucro_vendas(snap)
        payload = {
            "valor_total_em_stock": str(e.valor_total_em_stock),
            "total_receita": str(v.total_receita),
            "total_cmv": str(v.total_custo_mercadoria_vendida),
            "lucro_bruto": str(v.lucro_bruto),
            "num_linhas_venda": len(v.detalhe_por_linha),
            "num_skus_com_stock": len(e.linhas),
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    return [obter_relatorio_estoque_json, obter_relatorio_vendas_lucro_json, obter_indicadores_consolidados_json]


_SYSTEM = """És **analista de retalho** para um mercantil de bairro. Tens acesso a ferramentas que devolvem dados **estruturados (JSON)** gerados a partir do sistema da loja (Pydantic).

Regras:
- **Chama as ferramentas** antes de concluir: pelo menos o relatório de stock e o de vendas/lucro, para a tua análise assentar em números correctos.
- Escreve em **português europeu**, tom profissional e directo.
- Resposta final com secções numeradas:
  1. **Stock** — cobertura por SKU, valor imobilizado, risco de rutura ou excesso.
  2. **Vendas** — mix por produto/nota, preços efectivos vs catálogo quando relevante.
  3. **Lucro e margem** — lucro bruto, CMV, margens por linha que mais pesam.
  4. **Recomendações** — 3 a 5 acções concretas (compras, promoções, revisão de preço, reposição).

Cita valores e SKUs quando útil. Não inventes números que não apareçam nos JSON das tools."""


def criar_grafo_analise_mercantil(loja: Mercantil) -> Any:
    """Grafo ReAct com `MemorySaver` (histórico por `thread_id`)."""
    _garantir_chave_api()
    llm = ChatGoogleGenerativeAI(model=_modelo(), temperature=0.25)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return create_react_agent(
        llm,
        tools=criar_ferramentas_mercantil(loja),
        prompt=prompt,
        checkpointer=MemorySaver(),
    )


def config_analise(thread_id: str = "ex20-analise-mercantil") -> dict:
    return {"configurable": {"thread_id": thread_id}}


def ultima_resposta_texto(resultado: dict) -> str:
    msgs = resultado.get("messages") or []
    for m in reversed(msgs):
        if isinstance(m, AIMessage) and (m.content or "").strip():
            c = m.content
            return c if isinstance(c, str) else str(c)
    return ""
