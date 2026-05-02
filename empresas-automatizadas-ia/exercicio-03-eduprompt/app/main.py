"""EduPrompt Academy — API FastAPI opcional sobre as chains LCEL."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.chains.eduprompt_chains import chain_narrativa_nerd, gerar_pacote_educacional


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

app = FastAPI(
    title="EduPrompt Academy",
    version="1.0.0",
    description="Três chains LCEL (explicação, exercícios, resumo) + narrativa nerd opcional.",
)


class EduEntrada(BaseModel):
    tema: str = Field(examples=["RAG"])
    nivel: str = Field(default="iniciante", examples=["iniciante"])


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "exercicio": 3,
        "empresa": "EduPrompt Academy",
        "chains": ["explicacao", "exercicios", "resumo", "narrativa_nerd_opcional"],
    }


@app.post("/eduprompt/pacote")
def post_pacote(body: EduEntrada) -> dict[str, str]:
    """Gera explicação, exercícios e resumo; devolve também `markdown` consolidado."""
    return gerar_pacote_educacional(body.model_dump(), paralelo=True)


@app.post("/eduprompt/narrativa-nerd")
def post_narrativa_nerd(body: EduEntrada) -> dict[str, str]:
    """Desafio extra — narrativa sarcástica nerd sobre o tema."""
    texto = chain_narrativa_nerd().invoke(body.model_dump())
    return {"tema": body.tema, "nivel": body.nivel, "narrativa": texto}


def main() -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    main()
