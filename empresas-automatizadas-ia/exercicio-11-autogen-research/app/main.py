"""Exercício 11 — AutoGen Research Lab: debate multiagente + API."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.autogen_flow import executar_debate


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

app = FastAPI(title="AutoGen Research Lab", version="1.0.0")


class DebateIn(BaseModel):
    tema: str = Field(..., min_length=4, description="Tema ou pergunta de pesquisa.")
    rodadas: int = Field(4, ge=1, le=20, description="Controla extensão do debate (desafio extra).")


class DebateOut(BaseModel):
    relatorio_final: str
    mensagens: list[dict]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "exercicio": 11, "empresa": "AutoGen Research Lab"}


@app.post("/debate", response_model=DebateOut)
def debate(body: DebateIn) -> DebateOut:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="Defina GOOGLE_API_KEY no ambiente.")
    try:
        out = executar_debate(body.tema.strip(), rodadas=body.rodadas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return DebateOut(relatorio_final=out["relatorio_final"], mensagens=out["log"])


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
