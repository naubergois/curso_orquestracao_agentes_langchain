"""Schemas Pydantic — entrada da API e saída estruturada validada (Instructor + Gemini)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TextoDemandaIn(BaseModel):
    """Corpo HTTP POST `/analisar`."""

    texto: str = Field(
        ...,
        min_length=40,
        description="Narrativa ou peça informal enviada pelo cliente interno.",
    )


class ScreeningJuridico(BaseModel):
    """Gate obrigatório antes da extração completa (desafio extra: bloquear não-jurídico)."""

    texto_refere_questao_juridica: bool = Field(
        ...,
        description="True se existir contexto jurídico relevante (contrato, litígio, prazo legal, etc.).",
    )
    confianca: Literal["baixa", "media", "alta"] = Field(
        default="media",
        description="Confiança na classificação anterior.",
    )
    motivo: str = Field(
        ...,
        max_length=600,
        description="Justificação curta em português europeu.",
    )


class DemandaExtraida(BaseModel):
    """JSON final após LLM + validação Pydantic."""

    tipo_demanda: str = Field(
        ...,
        description="Categoria principal (ex.: contratual, trabalhista, consumerista).",
        examples=["contratual"],
    )
    partes_envolvidas: list[str] = Field(
        default_factory=list,
        description="Nomes ou designações mencionadas (pessoas singulares ou empresas).",
    )
    prazo: str | None = Field(
        None,
        description="Prazos, datas ou urgências mencionadas; texto curto.",
    )
    risco: Literal["baixo", "medio", "alto"] = Field(
        ...,
        description="Risco inferido de forma conservadora.",
    )
    prioridade: Literal["baixa", "media", "alta"] = Field(
        ...,
        description="Prioridade operacional sugerida.",
    )
    resumo: str = Field(
        ...,
        min_length=20,
        max_length=2500,
        description="Síntese factual sem aconselhamento jurídico definitivo.",
    )
