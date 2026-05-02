"""Exercício 16 — ObservaAI: experimentos, MLflow, LangSmith opcional, resultados para Streamlit."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.experimentos import correr_entrada


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

app = FastAPI(title="ObservaAI", version="1.0.0")


class ExpIn(BaseModel):
    entrada: str = Field(..., min_length=2)
    avaliacao_manual: str | None = Field(None, description="Opcional: nota textual ou score")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "exercicio": 16, "empresa": "ObservaAI"}


@app.post("/experimentos")
def experimentos(body: ExpIn) -> dict:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="Defina GOOGLE_API_KEY.")
    try:
        return correr_entrada(body.entrada.strip(), body.avaliacao_manual)
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
