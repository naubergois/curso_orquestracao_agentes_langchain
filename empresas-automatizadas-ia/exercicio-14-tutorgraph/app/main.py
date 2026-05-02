"""Exercício 14 — TutorGraph: grafo LangGraph + estado tipado (Pydantic na API)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from app.schemas import TutorPedido, TutorResultado
from app.tutor_graph import executar_sessao


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

app = FastAPI(title="TutorGraph", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "exercicio": 14, "empresa": "TutorGraph"}


@app.post("/sessao", response_model=TutorResultado)
def sessao(body: TutorPedido) -> TutorResultado:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="Defina GOOGLE_API_KEY.")
    try:
        raw = executar_sessao(body.tema.strip(), body.resposta_aluno.strip(), body.nivel.strip())
        return TutorResultado.model_validate(raw)
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
