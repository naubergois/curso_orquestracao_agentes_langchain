"""Exercício 15 — AuditoriaGraph: LangGraph + LangSmith (variáveis de ambiente)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.audit_graph import executar


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

app = FastAPI(title="AuditoriaGraph", version="1.0.0")


class AchadoIn(BaseModel):
    texto: str = Field(..., min_length=10, description="Descrição do achado de auditoria.")


@app.get("/health")
def health() -> dict:
    tracing = bool(os.environ.get("LANGCHAIN_TRACING_V2", "").lower() in ("1", "true", "yes"))
    return {
        "status": "ok",
        "exercicio": 15,
        "empresa": "AuditoriaGraph",
        "langsmith_tracing_env": tracing,
    }


@app.post("/analisar")
def analisar(body: AchadoIn) -> dict:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="Defina GOOGLE_API_KEY.")
    try:
        return executar(body.texto)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


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
