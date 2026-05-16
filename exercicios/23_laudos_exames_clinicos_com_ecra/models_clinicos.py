"""Modelos Pydantic para avaliação de gravidade (dados fictícios / formação)."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class NivelGravidade(str, Enum):
    baixa = "baixa"
    moderada = "moderada"
    elevada = "elevada"
    critica = "critica"


class AvaliacaoGravidade(BaseModel):
    """Saída estruturada do agente avaliador (LangGraph + Gemini)."""

    paciente_id: int = Field(..., ge=1, le=9999)
    nivel: NivelGravidade
    score_0_100: int = Field(..., ge=0, le=100, description="Risco agregado 0=baixo, 100=máximo no cenário-demo.")
    hipoteses_patologicas: list[str] = Field(
        default_factory=list,
        max_length=8,
        description="Hipóteses a correlacionar com quadro clínico; não são diagnósticos.",
    )
    achados_laboratoriais_chave: list[str] = Field(
        default_factory=list,
        max_length=12,
        description="Bullets com valores ou padrões relevantes do laudo.",
    )
    riscos_imediatos: list[str] = Field(
        default_factory=list,
        max_length=8,
        description="Riscos a vigilar (ex.: arritmogenicidade, disfunção renal aguda).",
    )
    perguntas_para_o_clinico: list[str] = Field(
        default_factory=list,
        max_length=6,
        description="Perguntas de refinamento para o médico assistente.",
    )
    conduta_sugerida_formacao: str = Field(
        ...,
        max_length=2000,
        description="Sugestões pedagógicas; não substituem protocolo institucional.",
    )
    disclaimer: str = Field(
        default="Conteúdo gerado por IA sobre dados fictícios — não usar como parecer médico real.",
        max_length=500,
    )
