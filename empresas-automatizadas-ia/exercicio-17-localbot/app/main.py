"""Exercício 17 — LocalBot: LangChain + Ollama (e comparação opcional com API)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.chat_local import chat_cloud, chat_local


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

app = FastAPI(title="LocalBot", version="1.0.0")


class Msg(BaseModel):
    mensagem: str = Field(..., min_length=1)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "exercicio": 17, "empresa": "LocalBot"}


@app.post("/chat")
def chat(body: Msg) -> dict:
    try:
        out = chat_local(body.mensagem.strip())
        return {"origem": "ollama", "resposta": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/chat/compare")
def compare(body: Msg) -> dict:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=400, detail="GOOGLE_API_KEY necessário para /chat/compare.")
    try:
        loc = chat_local(body.mensagem.strip())
        clo = chat_cloud(body.mensagem.strip())
        return {"local": loc, "nuvem": clo}
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
