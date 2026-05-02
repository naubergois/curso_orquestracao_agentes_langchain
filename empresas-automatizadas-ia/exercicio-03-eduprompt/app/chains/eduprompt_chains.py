"""EduPrompt Academy — chains LCEL reutilizáveis (PromptTemplate → modelo → StrOutputParser).

Para modelos de *chat* (Gemini) usamos ``ChatPromptTemplate`` de ``langchain_core.prompts``:
é o análogo composável de ``PromptTemplate`` aplicado a mensagens ``system`` / ``human``.
"""

from __future__ import annotations

import os
from functools import lru_cache

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel
from langchain_google_genai import ChatGoogleGenerativeAI


@lru_cache(maxsize=1)
def _llm_padrao() -> ChatGoogleGenerativeAI:
    model = (os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", "")
    return ChatGoogleGenerativeAI(model=model, temperature=0.25)


# --- Templates (variáveis: tema, nivel) ---

PROMPT_EXPLICACAO = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "És o EduPrompt Academy. Escreve em português europeu, tom professoral e claro. "
            "Adaptas vocabulário e profundidade ao nível pedido (iniciante, intermédio ou avançado).",
        ),
        (
            "human",
            "Explica o tema «{tema}» para um público de nível «{nivel}».\n"
            "Usa 2–4 parágrafos curtos. Começa por contextualizar o tema numa frase.\n"
            "Não uses cabeçalhos Markdown (##) no texto; só parágrafos e listas curtas se ajudarem.",
        ),
    ]
)

PROMPT_EXERCICIOS = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "És o EduPrompt Academy. Crias exercícios objetivos em português europeu.",
        ),
        (
            "human",
            "Cria **três** exercícios sobre «{tema}», adequados ao nível «{nivel}».\n"
            "Numera exatamente assim: `1.`, `2.`, `3.` — uma linha ou parágrafo curto por exercício.\n"
            "Sem cabeçalhos Markdown.",
        ),
    ]
)

PROMPT_RESUMO = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "És o EduPrompt Academy. Resumes com rigor em português europeu.",
        ),
        (
            "human",
            "Resume «{tema}» para nível «{nivel}» em 4 a 6 bullet points.\n"
            "Cada linha começa por `- `. Sem cabeçalhos Markdown.",
        ),
    ]
)

PROMPT_NARRATIVA_NERD = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Humor nerd e sarcástico **leve**; não insultes grupos nem pessoas. Mantém correção técnica.",
        ),
        (
            "human",
            "Escreve **um único parágrafo** (até ~120 palavras) sobre «{tema}», "
            "como se fossem duas equipas (Produto vs Engenharia) a «lutar» pelo mesmo buzzword, "
            "para um leitor «{nivel}». Tom ironico corporativo de TI.",
        ),
    ]
)


def llm_eduprompt() -> ChatGoogleGenerativeAI:
    """Expõe o modelo cacheado (útil para testes e FastAPI)."""
    return _llm_padrao()


def chain_explicacao(llm: ChatGoogleGenerativeAI | None = None) -> Runnable:
    """Pipeline: template de explicação → modelo → texto."""
    return PROMPT_EXPLICACAO | (llm or _llm_padrao()) | StrOutputParser()


def chain_exercicios(llm: ChatGoogleGenerativeAI | None = None) -> Runnable:
    """Pipeline: template de exercícios → modelo → texto."""
    return PROMPT_EXERCICIOS | (llm or _llm_padrao()) | StrOutputParser()


def chain_resumo(llm: ChatGoogleGenerativeAI | None = None) -> Runnable:
    """Pipeline: template de resumo → modelo → texto."""
    return PROMPT_RESUMO | (llm or _llm_padrao()) | StrOutputParser()


def chain_narrativa_nerd(llm: ChatGoogleGenerativeAI | None = None) -> Runnable:
    """Desafio extra: narrativa sarcástica nerd sobre o tema."""
    return PROMPT_NARRATIVA_NERD | (llm or _llm_padrao()) | StrOutputParser()


def parallel_educacional(llm: ChatGoogleGenerativeAI | None = None) -> RunnableParallel:
    """Executa as três chains principais em paralelo (mesmo ``invoke`` com ``tema`` e ``nivel``)."""
    m = llm or _llm_padrao()
    return RunnableParallel(
        explicacao=chain_explicacao(m),
        exercicios=chain_exercicios(m),
        resumo=chain_resumo(m),
    )


def montar_markdown_pacote(partes: dict[str, str]) -> str:
    """Junta as três saídas no formato do enunciado (## Explicação, ## Exercícios, ## Resumo)."""
    return (
        "## Explicação\n\n"
        f"{partes['explicacao'].strip()}\n\n"
        "## Exercícios\n\n"
        f"{partes['exercicios'].strip()}\n\n"
        "## Resumo\n\n"
        f"{partes['resumo'].strip()}"
    )


def gerar_pacote_educacional(
    vars_: dict[str, str],
    *,
    llm: ChatGoogleGenerativeAI | None = None,
    paralelo: bool = True,
) -> dict[str, str]:
    """
    Entrada típica: ``{\"tema\": \"RAG\", \"nivel\": \"iniciante\"}``.
    Devolve chaves ``explicacao``, ``exercicios``, ``resumo``, ``markdown``.
    """
    if paralelo:
        out = parallel_educacional(llm).invoke(vars_)
    else:
        out = {
            "explicacao": chain_explicacao(llm).invoke(vars_),
            "exercicios": chain_exercicios(llm).invoke(vars_),
            "resumo": chain_resumo(llm).invoke(vars_),
        }
    md = montar_markdown_pacote(out)
    return {**out, "markdown": md}
