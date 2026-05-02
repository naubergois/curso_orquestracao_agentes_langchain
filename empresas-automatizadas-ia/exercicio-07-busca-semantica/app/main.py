"""Busca Semântica Ltda. — FAISS + Hugging Face Transformers."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.embeddings_hf import EmbedderHF, caminho_documentos
from app.faiss_store import busca_palavra_chave, buscar_semantico, carregar_indice


def _carregar_env() -> None:
    ex = Path(__file__).resolve().parents[1]
    load_dotenv(ex.parent.parent / ".env", override=False)
    load_dotenv(ex / ".env", override=True)


_carregar_env()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Busca Semântica Ltda.",
    version="1.0.0",
    description="Embeddings via Transformers + índice FAISS (top‑5).",
)


class PerguntaIn(BaseModel):
    pergunta: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)


class DocScore(BaseModel):
    documento: str
    score: float


@lru_cache(maxsize=1)
def _embedder() -> EmbedderHF:
    mid = os.environ.get("HF_EMBEDDING_MODEL", "").strip() or (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    return EmbedderHF(model_id=mid)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "exercicio": 7, "empresa": "Busca Semântica Ltda."}


@app.post("/buscar", response_model=list[DocScore])
def buscar(body: PerguntaIn) -> list[DocScore]:
    """Top‑k documentos mais parecidos (similaridade coseno via produto interno)."""
    try:
        carregar_indice()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    try:
        qv = _embedder().encode([body.pergunta.strip()])
        hits = buscar_semantico(qv[0], k=body.top_k)
        return [DocScore(**h) for h in hits]
    except Exception as e:
        logger.exception("buscar")
        raise HTTPException(status_code=500, detail=str(e)[:500]) from e


@app.get("/comparar")
def comparar(
    pergunta: str = Query(..., min_length=3),
    top_k: int = Query(5, ge=1, le=20),
) -> dict:
    """Desafio extra: semântico vs palavra‑chave."""
    try:
        _, nomes = carregar_indice()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    docs_dir = caminho_documentos()
    textos = [(docs_dir / n).read_text(encoding="utf-8") for n in nomes]
    qv = _embedder().encode([pergunta.strip()])
    return {
        "pergunta": pergunta,
        "semantico": buscar_semantico(qv[0], k=top_k),
        "palavra_chave": busca_palavra_chave(textos, nomes, pergunta, k=top_k),
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
