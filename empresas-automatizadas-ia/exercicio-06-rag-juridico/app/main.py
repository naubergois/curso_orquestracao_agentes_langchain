"""RAG Jurídico — API FastAPI (Exercício 6) + pipeline LlamaIndex/Chroma."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.rag.pipeline import consultar_com_fontes


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Jurídico",
    version="1.0.0",
    description=(
        "Empresa simulada **RAG Jurídico**: consulta semântica sobre documentos internos fictícios "
        "(LlamaIndex + ChromaDB + Gemini)."
    ),
)


class PerguntaIn(BaseModel):
    pergunta: str = Field(..., min_length=6, description="Pergunta sobre os documentos indexados.")
    top_k: int = Field(default=5, ge=1, le=20, description="Fragmentos a recuperar.")


class FonteOut(BaseModel):
    score: float | None = None
    arquivo: str
    trecho: str


class RespostaRAGOut(BaseModel):
    resposta: str
    fontes: list[FonteOut]


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "exercicio": 6,
        "empresa": "RAG Jurídico",
        "llm": (os.environ.get("GEMINI_MODEL_EX06") or os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace(
            "models/", ""
        ),
        "embedding": (
            os.environ.get("GEMINI_EMBEDDING_MODEL_EX06")
            or os.environ.get("GEMINI_EMBEDDING_MODEL")
            or "gemini-embedding-001"
        ).replace("models/", ""),
        "nota": "Execute `python scripts/indexar.py` antes da primeira consulta.",
    }


@app.post("/perguntar", response_model=RespostaRAGOut)
def perguntar(body: PerguntaIn) -> RespostaRAGOut:
    """Pergunta → retriever Chroma → resposta com contexto + lista de fontes (trechos)."""
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_API_KEY em falta no ambiente.",
        )
    try:
        raw = consultar_com_fontes(body.pergunta.strip(), top_k=body.top_k)
    except Exception as e:
        logger.exception("Falha na consulta RAG")
        msg = str(e).lower()
        if "does not exist" in msg or "no collection" in msg or "was not found" in msg:
            raise HTTPException(
                status_code=503,
                detail="Índice Chroma inexistente. No contentor ou host: `python scripts/indexar.py`.",
            ) from e
        raise HTTPException(status_code=503, detail=str(e)[:800]) from e

    return RespostaRAGOut(
        resposta=raw["resposta"],
        fontes=[FonteOut(**f) for f in raw["fontes"]],
    )


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
