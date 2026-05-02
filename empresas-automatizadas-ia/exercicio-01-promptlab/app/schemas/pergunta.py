"""Schemas de entrada e saída da PromptLab Consultoria."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class PerfilAssistente(str, Enum):
    """Perfis de sistema disponíveis para o assistente."""

    tecnico = "tecnico"
    professor = "professor"
    comercial = "comercial"
    sarcastico_nerd = "sarcastico_nerd"


class PerguntaEntrada(BaseModel):
    """Corpo JSON esperado pelo endpoint principal."""

    perfil: PerfilAssistente = Field(
        ...,
        description="Perfil do assistente: tecnico, professor, comercial ou sarcastico_nerd.",
    )
    pergunta: str = Field(
        ...,
        min_length=1,
        max_length=8000,
        description="Pergunta ou instrução do utilizador.",
    )


class RespostaSaida(BaseModel):
    """Resposta estruturada devolvida pela API."""

    perfil: str
    resposta: str
