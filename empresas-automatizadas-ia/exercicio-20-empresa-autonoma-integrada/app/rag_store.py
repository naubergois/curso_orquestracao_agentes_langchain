"""RAG com Chroma persistente e embeddings Google."""

from __future__ import annotations

import os
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

_ROOT = Path(__file__).resolve().parents[1]
_DOCS = _ROOT / "data" / "documentos"
_CHROMA = _ROOT / "chroma_data"

_vs: Chroma | None = None
_INDEX_FLAG = _CHROMA / ".indexed_ok"


def _embeddings():
    model = os.environ.get("GEMINI_EMBED_MODEL", "gemini-embedding-001").replace("models/", "")
    return GoogleGenerativeAIEmbeddings(model=model)


def _carregar_documentos() -> list[Document]:
    docs: list[Document] = []
    if not _DOCS.exists():
        return docs
    for path in sorted(_DOCS.glob("*.md")):
        txt = path.read_text(encoding="utf-8")
        docs.append(Document(page_content=txt, metadata={"fonte": path.name}))
    return docs


def get_vectorstore() -> Chroma:
    global _vs
    if _vs is not None:
        return _vs
    emb = _embeddings()
    _CHROMA.mkdir(parents=True, exist_ok=True)
    _vs = Chroma(
        embedding_function=emb,
        persist_directory=str(_CHROMA),
        collection_name="empresa_autonoma",
    )
    if not _INDEX_FLAG.exists():
        raw_docs = _carregar_documentos()
        splitter = RecursiveCharacterTextSplitter(chunk_size=450, chunk_overlap=80)
        chunks = splitter.split_documents(raw_docs) if raw_docs else []
        if chunks:
            _vs.add_documents(chunks)
        _INDEX_FLAG.write_text("1", encoding="utf-8")
    return _vs


def formatar_contexto(pergunta: str, k: int = 4) -> str:
    vs = get_vectorstore()
    pairs = vs.similarity_search_with_score(pergunta, k=k)
    blocos = []
    for doc, score in pairs:
        fonte = doc.metadata.get("fonte", "?")
        blocos.append(f"[{fonte} | score={score:.4f}]\n{doc.page_content}")
    return "\n\n---\n\n".join(blocos) if blocos else "(Sem documentos indexados.)"
