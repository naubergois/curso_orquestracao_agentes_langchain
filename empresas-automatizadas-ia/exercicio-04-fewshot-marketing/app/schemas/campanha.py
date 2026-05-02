"""Schema Pydantic da campanha e pedido à API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

EstiloPreset = Literal["livre", "formal", "engracado", "tecnico", "provocativo"]

ESTILO_PARA_INSTRUCAO: dict[str, str] = {
    "livre": "Segue apenas as notas de tom indicadas pelo cliente (sem preset rígido).",
    "formal": "Tom institucional e credível; vocabulário cuidado; evita gírias e ironia pesada.",
    "engracado": "Tom leve e espirituoso (nível LinkedIn/Twitter profissional); sem crueldade nem estereótipos.",
    "tecnico": "Tom preciso com termos da área; assume público que tolera detalhe; poucos adjetivos vazios.",
    "provocativo": "Contraste forte, perguntas incómodas e urgência inteligente — sem insultos, discriminação ou desinformação.",
}


class Campanha(BaseModel):
    """Modelo de saída esperado — validação pós-LLM (Instructor + Pydantic)."""

    titulo: str = Field(..., max_length=140, description="Título ou gancho principal")
    publico_alvo: str = Field(..., description="Quem deve ler e responder")
    tom: str = Field(..., description="Tom efectivo usado no texto")
    texto_post: str = Field(..., min_length=40, description="Corpo principal do post")
    chamada_para_acao: str = Field(..., min_length=4, description="CTA explícita")
    hashtags: list[str] = Field(..., min_length=3, max_length=12, description="Lista de hashtags")

    @field_validator("hashtags", mode="before")
    @classmethod
    def normalizar_hashtags(cls, v: object) -> object:
        if not isinstance(v, list):
            return v
        out: list[str] = []
        for item in v:
            if not isinstance(item, str):
                continue
            t = item.strip()
            if not t:
                continue
            if not t.startswith("#"):
                t = "#" + t.lstrip("#")
            out.append(t)
        return out

    @model_validator(mode="after")
    def texto_coerente(self) -> Campanha:
        if len(self.texto_post.strip()) < 40:
            raise ValueError("texto_post demasiado curto para uma campanha útil")
        return self


class GerarCampanhaEntrada(BaseModel):
    """Corpo JSON da API — alinhado com o enunciado + desafio extra (`estilo`)."""

    produto: str = Field(..., min_length=3, examples=["curso de agentes inteligentes"])
    publico: str = Field(..., min_length=3, examples=["profissionais de tecnologia"])
    tom: str = Field(
        default="didático e próximo",
        description="Notas livres de tom (ex.: «didático e sarcástico»). Combina com `estilo`.",
    )
    estilo: EstiloPreset = Field(
        default="livre",
        description="Preset: livre | formal | engracado | tecnico | provocativo",
    )
