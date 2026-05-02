"""HelpDesk Agent — LangChain tools + LangGraph ReAct."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.agent_core import chat_turn


def _env() -> None:
    r = Path(__file__).resolve().parents[1]
    load_dotenv(r.parent.parent / ".env", override=False)
    load_dotenv(r / ".env", override=True)


_env()

app = FastAPI(title="HelpDesk Agent", version="1.0.0")


class ChatIn(BaseModel):
    mensagem: str = Field(..., min_length=3)
    thread_id: str = Field(default="default")


class ChatOut(BaseModel):
    resposta: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "exercicio": 9, "empresa": "HelpDesk Agent"}


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn) -> ChatOut:
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        raise HTTPException(status_code=503, detail="GOOGLE_API_KEY em falta.")
    try:
        txt = chat_turn(body.mensagem.strip(), body.thread_id.strip() or "default")
        return ChatOut(resposta=txt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)[:800]) from e


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))


if __name__ == "__main__":
    main()
