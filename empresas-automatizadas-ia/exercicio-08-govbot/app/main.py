"""GovBot Cidadão — Haystack + Qdrant + Gemini."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.govbot_service import responder


def _env() -> None:
    r = Path(__file__).resolve().parents[1]
    load_dotenv(r.parent.parent / ".env", override=False)
    load_dotenv(r / ".env", override=True)


_env()

app = FastAPI(title="GovBot Cidadão", version="1.0.0")


class ChatIn(BaseModel):
    mensagem: str = Field(..., min_length=4)


class FonteOut(BaseModel):
    documento: str
    excerto: str


class ChatOut(BaseModel):
    classificacao_demanda: str
    resposta: str
    fontes: list[FonteOut]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "exercicio": 8, "empresa": "GovBot Cidadão", "qdrant": os.environ.get("QDRANT_URL")}


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn) -> ChatOut:
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        raise HTTPException(status_code=503, detail="GOOGLE_API_KEY em falta.")
    try:
        raw = responder(body.mensagem.strip())
        return ChatOut(
            classificacao_demanda=raw["classificacao_demanda"],
            resposta=raw["resposta"],
            fontes=[FonteOut(**f) for f in raw["fontes"]],
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e)[:900]) from e


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))


if __name__ == "__main__":
    main()
