"""Esqueleto — Exercício 17: LocalBot. Implemente o enunciado completo."""

from __future__ import annotations

import os

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

app = FastAPI(title="LocalBot", version="0.0.0")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "exercicio": 17,
        "empresa": "LocalBot",
        "nota": "Esqueleto funcional — desenvolver chains, agents, vector DB, etc., conforme o enunciado.",
    }


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
