"""Exercício 12 — Semantic Kernel Office: skills administrativas via API."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.office_skills import SkillNome, executar_skill


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

app = FastAPI(title="Semantic Kernel Office", version="1.0.0")


class ExecutarIn(BaseModel):
    skill: SkillNome = Field(..., description="resumir | email | tarefas | reuniao (composta)")
    texto: str = Field(..., min_length=3)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "exercicio": 12, "empresa": "Semantic Kernel Office"}


@app.post("/executar")
async def executar(body: ExecutarIn) -> dict:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="Defina GOOGLE_API_KEY.")
    try:
        return await executar_skill(body.skill, body.texto)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/executar_sync")
def executar_sync(body: ExecutarIn) -> dict:
    return asyncio.run(executar_skill(body.skill, body.texto))


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
