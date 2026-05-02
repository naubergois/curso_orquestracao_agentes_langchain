"""Chains LCEL — EduPrompt Academy."""

from app.chains.eduprompt_chains import (
    PROMPT_EXERCICIOS,
    PROMPT_EXPLICACAO,
    PROMPT_NARRATIVA_NERD,
    PROMPT_RESUMO,
    chain_exercicios,
    chain_explicacao,
    chain_narrativa_nerd,
    chain_resumo,
    gerar_pacote_educacional,
    llm_eduprompt,
    montar_markdown_pacote,
    parallel_educacional,
)

__all__ = [
    "PROMPT_EXERCICIOS",
    "PROMPT_EXPLICACAO",
    "PROMPT_NARRATIVA_NERD",
    "PROMPT_RESUMO",
    "chain_exercicios",
    "chain_explicacao",
    "chain_narrativa_nerd",
    "chain_resumo",
    "gerar_pacote_educacional",
    "llm_eduprompt",
    "montar_markdown_pacote",
    "parallel_educacional",
]
