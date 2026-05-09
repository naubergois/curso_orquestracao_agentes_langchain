"""Exercício 17 — notícias do dia: pesquisa Web, dados estruturados (Pydantic), resumo executivo (agentes Gemini)."""

from __future__ import annotations

import os
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field, field_validator


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_local_env()


# Categorias em texto simples (evita *enum* no JSON Schema do Gemini — limite de estados).
_CATEGORIAS = frozenset(
    {
        "politica",
        "economia",
        "tecnologia",
        "ciencia_saude",
        "desporto",
        "internacional",
        "sociedade",
        "outra",
    }
)


class NoticiaItem(BaseModel):
    """Modelo mínimo para `with_structured_output` (Gemini rejeita schemas muito ricos)."""

    titulo: str
    url: str | None = None
    fonte: str | None = None
    resumo_curto: str
    categoria: str
    relevancia_0_10: int = 5

    @field_validator("categoria")
    @classmethod
    def _cat(cls, v: str) -> str:
        x = (v or "outra").strip().lower().replace(" ", "_").replace("-", "_")
        return x if x in _CATEGORIAS else "outra"

    @field_validator("relevancia_0_10")
    @classmethod
    def _rel(cls, v: int) -> int:
        return max(0, min(10, int(v)))


class BoletimNoticias(BaseModel):
    data_referencia: str
    consulta_original: str
    itens: list[NoticiaItem] = Field(default_factory=list)


class ResumoExecutivo(BaseModel):
    headline: str
    pontos_chave: list[str] = Field(default_factory=list)
    riscos_ou_incertezas: list[str] = Field(default_factory=list)
    oportunidades_ou_acoes: list[str] = Field(default_factory=list)
    disclaimer: str = "Confirmar nas fontes; resumo automático pedagógico."


class IndicadoresBoletim(BaseModel):
    total_noticias: int
    contagem_por_categoria: dict[str, int]
    relevancia_media: float
    fraccao_internacional: float
    diversidade_categorias: int
    titulo_maior_relevancia: str | None = None


def _ensure_google_key() -> None:
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        raise RuntimeError(
            "Defina GOOGLE_API_KEY (ou GEMINI_API_KEY) no `.env` na raiz do repositório para o exercício 17."
        )


def build_chat_model(*, temperature: float = 0.25) -> ChatGoogleGenerativeAI:
    _ensure_google_key()
    key = (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()
    os.environ.setdefault("GOOGLE_API_KEY", key)
    default = "gemini-2.0-flash"
    nome = (os.environ.get("GEMINI_MODEL_EX17") or os.environ.get("GEMINI_MODEL") or default).strip()
    nome = nome.removeprefix("models/")
    if nome.startswith("gemini-1.5"):
        nome = default
    return ChatGoogleGenerativeAI(model=nome, temperature=temperature)


@tool
def pesquisa_noticias_web(consulta: str) -> str:
    """Pesquisa na Web via DuckDuckGo (notícias e páginas). Consulta curta em português, ex.: 'notícias Portugal hoje'."""
    from langchain_community.tools import DuckDuckGoSearchResults

    search = DuckDuckGoSearchResults(max_results=10)
    try:
        raw = search.invoke(consulta)
    except Exception:
        raw = search.invoke({"query": consulta})
    return raw if isinstance(raw, str) else str(raw)


def build_agente_pesquisa():
    """Agente ReAct com uma única tool: resultados DuckDuckGo (rede necessária)."""
    llm = build_chat_model(temperature=0.35)
    sys = SystemMessage(
        content="""És um **jornalista de agência** focado em factos recentes.

Regras:
- Usa **apenas** a ferramenta `pesquisa_noticias_web` para obter trechos da Web (não inventes URLs).
- Faz **2 a 4** pesquisas complementares se precisares de cobrir economia, política e sociedade.
- No texto final, lista **manchetes** com uma linha de contexto cada e, quando existir, o URL ou domínio indicado nos resultados.
- Escreve em **português europeu**, tom neutro e conciso.
- Não alegues teres acesso a leis internas ou fontes fechadas: só o que a pesquisa devolver."""
    )
    return create_agent(
        llm,
        tools=[pesquisa_noticias_web],
        system_prompt=sys,
        checkpointer=MemorySaver(),
    )


def build_agente_redator_resumo():
    """Agente sem tools: transforma boletim estruturado em narrativa executiva (Markdown)."""
    llm = build_chat_model(temperature=0.4)
    sys = SystemMessage(
        content="""És um **consultor de direcção** que escreve **resumos executivos** para CEO.

Entrada: JSON de notícias já estruturadas (Pydantic serializado).
Saída: **Markdown** com:
1. Título `## Resumo executivo`
2. Parágrafo inicial (4–6 linhas) com o essencial do dia
3. Secção `### Pontos de atenção` com marcadores
4. Secção `### Leituras recomendadas` (até 5 bullets com tema, sem inventar links novos)

Tom: português europeu, directo, sem sensacionalismo."""
    )
    return create_agent(
        llm,
        tools=[],
        system_prompt=sys,
        checkpointer=MemorySaver(),
    )


def executar_turno(graph: Any, mensagem: str, thread_id: str) -> str:
    cfg: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
    out = graph.invoke({"messages": [HumanMessage(content=mensagem)]}, cfg)
    msgs = out.get("messages") or []
    for m in reversed(msgs):
        if isinstance(m, AIMessage):
            c = m.content
            return c if isinstance(c, str) else str(c)
    return "(sem resposta do modelo)"


def extrair_boletim_estruturado(llm: ChatGoogleGenerativeAI, texto_pesquisa: str, consulta: str) -> BoletimNoticias:
    """Usa saída estruturada Pydantic a partir do relatório textual do agente de pesquisa."""
    hoje = date.today().isoformat()
    structured = llm.with_structured_output(BoletimNoticias)
    msg = HumanMessage(
        content=f"""Converta o relatório abaixo num **BoletimNoticias** (Pydantic).

Regras:
- `data_referencia`: use {hoje} salvo indicação explícita contrária no texto.
- `consulta_original`: repita exactamente: {consulta!r}
- Cada item deve refletir **apenas** informação presente no relatório (não crie factos).
- `relevancia_0_10`: 0 = irrelevante para decisão, 10 = crítico para decisão.
- Limite a no máximo 12 itens mais informativos.

RELATÓRIO:
{texto_pesquisa}
"""
    )
    out = structured.invoke([msg])
    if not isinstance(out, BoletimNoticias):
        raise RuntimeError("Saída estruturada inesperada")
    return out


def extrair_resumo_executivo_pydantic(
    llm: ChatGoogleGenerativeAI, boletim: BoletimNoticias
) -> ResumoExecutivo:
    structured = llm.with_structured_output(ResumoExecutivo)
    msg = HumanMessage(
        content="Gere um **ResumoExecutivo** coerente com este boletim JSON:\n"
        + boletim.model_dump_json(indent=2)
    )
    out = structured.invoke([msg])
    if not isinstance(out, ResumoExecutivo):
        raise RuntimeError("ResumoExecutivo inválido")
    return out


def calcular_indicadores(boletim: BoletimNoticias) -> IndicadoresBoletim:
    itens = boletim.itens
    n = len(itens)
    if n == 0:
        return IndicadoresBoletim(
            total_noticias=0,
            contagem_por_categoria={},
            relevancia_media=0.0,
            fraccao_internacional=0.0,
            diversidade_categorias=0,
            titulo_maior_relevancia=None,
        )
    cats = [i.categoria for i in itens]
    cnt = Counter(cats)
    rel = sum(i.relevancia_0_10 for i in itens) / n
    inter = sum(1 for i in itens if i.categoria == "internacional")
    top = max(itens, key=lambda x: x.relevancia_0_10)
    return IndicadoresBoletim(
        total_noticias=n,
        contagem_por_categoria=dict(sorted(cnt.items())),
        relevancia_media=round(rel, 2),
        fraccao_internacional=round(inter / n, 3),
        diversidade_categorias=len(cnt),
        titulo_maior_relevancia=top.titulo[:200],
    )


def executar_pipeline_noticias(
    consulta: str | None = None,
    *,
    thread_pesquisa: str = "ex17-pesquisa",
    thread_redator: str = "ex17-redator",
) -> dict[str, Any]:
    """Orquestra pesquisa (agente + tool) → Pydantic → indicadores → resumo executivo (Pydantic + agente Markdown)."""
    consulta = (consulta or "notícias de hoje Portugal economia política sociedade").strip()
    pesq = build_agente_pesquisa()
    instrucao = (
        f"Prepara um relatório factual sobre: {consulta}. "
        "Garante variedade de temas (economia, política, sociedade ou internacional) se os resultados o permitirem."
    )
    relatorio = executar_turno(pesq, instrucao, thread_pesquisa)

    llm = build_chat_model(temperature=0.2)
    boletim = extrair_boletim_estruturado(llm, relatorio, consulta)
    indicadores = calcular_indicadores(boletim)
    resumo_pydantic = extrair_resumo_executivo_pydantic(llm, boletim)

    redator = build_agente_redator_resumo()
    markdown = executar_turno(
        redator,
        "Elabora o resumo executivo a partir deste JSON:\n" + boletim.model_dump_json(indent=2),
        thread_redator,
    )

    return {
        "consulta": consulta,
        "relatorio_pesquisa_bruto": relatorio,
        "boletim": boletim,
        "indicadores": indicadores,
        "resumo_executivo_estruturado": resumo_pydantic,
        "resumo_executivo_markdown": markdown,
    }
