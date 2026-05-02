"""Exercício 18 — API Agent Factory: FastAPI + LangChain + token opcional."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.chains import run_chat, run_classificar, run_resumir


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

app = FastAPI(title="API Agent Factory", version="1.0.0")
_bearer = HTTPBearer(auto_error=False)
_TOKEN = os.environ.get("API_TOKEN")


def _auth(creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]) -> None:
    if not _TOKEN:
        return
    if creds is None or creds.credentials != _TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido ou ausente (header Authorization: Bearer ...).")


class ChatIn(BaseModel):
    mensagem: str = Field(..., min_length=1)


class TextoIn(BaseModel):
    texto: str = Field(..., min_length=3)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "exercicio": 18, "empresa": "API Agent Factory", "auth_ativa": bool(_TOKEN)}


@app.post("/chat")
def chat(body: ChatIn, _: None = Depends(_auth)) -> dict:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="Defina GOOGLE_API_KEY.")
    try:
        return {"resposta": run_chat(body.mensagem.strip())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/classificar")
def classificar(body: TextoIn, _: None = Depends(_auth)) -> dict:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="Defina GOOGLE_API_KEY.")
    try:
        return {"resultado": run_classificar(body.texto.strip())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/resumir")
def resumir(body: TextoIn, _: None = Depends(_auth)) -> dict:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="Defina GOOGLE_API_KEY.")
    try:
        return {"resumo": run_resumir(body.texto.strip())}
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
