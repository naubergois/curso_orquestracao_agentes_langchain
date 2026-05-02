"""Contratos Pydantic (entrada/saída HTTP) espelhando o estado do tutor."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TutorPedido(BaseModel):
    tema: str = Field(..., min_length=2)
    resposta_aluno: str = ""
    nivel: str = "iniciante"


class TutorResultado(BaseModel):
    tema: str | None = None
    nivel: str | None = None
    diagnostico: str | None = None
    explicacao: str | None = None
    exercicio: str | None = None
    correto: bool | None = None
    feedback: str | None = None
    etapa_final: str | None = None
    logs: list[str] = Field(default_factory=list)
