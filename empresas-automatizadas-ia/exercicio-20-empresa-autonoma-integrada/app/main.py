"""Exercício 20 — Empresa Autónoma Integrada: API + LangGraph + RAG + observabilidade."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.empresa_graph import executar_pipeline


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

app = FastAPI(title="Empresa Autónoma Integrada", version="1.0.0")


class PipelineIn(BaseModel):
    mensagem: str = Field(..., min_length=3)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "exercicio": 20,
        "langsmith": bool(os.environ.get("LANGCHAIN_TRACING_V2")),
    }


@app.post("/pipeline")
def pipeline(body: PipelineIn) -> dict:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="Defina GOOGLE_API_KEY.")
    try:
        return executar_pipeline(body.mensagem)
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
