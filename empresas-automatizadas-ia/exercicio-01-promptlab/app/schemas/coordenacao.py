"""Coordenação multi-agente — vários padrões de orquestração entre perfis PromptLab."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ModoCoordenacao(str, Enum):
    """Padrões de coordenação entre agentes (cada um usa um perfil de sistema diferente)."""

    sequencial_pipeline = "sequencial_pipeline"
    paralelo_sintese = "paralelo_sintese"
    debate_critico = "debate_critico"
    router_inteligente = "router_inteligente"
    refinamento_triplo = "refinamento_triplo"


class CoordenacaoEntrada(BaseModel):
    pergunta: str = Field(..., min_length=1, max_length=8000)
    modo: ModoCoordenacao = Field(
        ...,
        description="Estratégia de coordenação entre agentes (perfis).",
    )


class EtapaCoordenacao(BaseModel):
    """Um passo observável na orquestração."""

    agente: str = Field(..., description="Identificador do agente / perfil.")
    papel: str = Field(..., description="Função nesta coordenação.")
    saida: str = Field(..., description="Texto produzido nesta etapa.")


class CoordenacaoSaida(BaseModel):
    modo: str
    resposta_final: str
    etapas: list[EtapaCoordenacao] = Field(default_factory=list)
