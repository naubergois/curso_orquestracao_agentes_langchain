"""Pipeline RAG: LlamaIndex + ChromaDB + Gemini (embeddings e LLM)."""

from __future__ import annotations

import os
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from llama_index.core import (
    Settings as LISettings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

COLECAO = "rag_juridico_docs"


def raiz_projeto() -> Path:
    """`exercicio-06-rag-juridico/`."""
    return Path(__file__).resolve().parents[2]


def dir_documentos() -> Path:
    return raiz_projeto() / "data" / "juridico"


def dir_chroma() -> Path:
    p = raiz_projeto() / "data" / "chroma_juridico"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _api_key() -> str:
    k = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not k:
        raise RuntimeError("Defina GOOGLE_API_KEY no `.env` na raiz do repositório do curso.")
    return k


def modelo_llm() -> str:
    raw = (
        os.environ.get("GEMINI_MODEL_EX06")
        or os.environ.get("GEMINI_MODEL")
        or "gemini-2.0-flash"
    )
    return raw.replace("models/", "").strip()


def normalize_gemini_embedding_model(raw: str) -> str:
    """Modelos como text-embedding-004 deixaram de existir em embedContent — usar gemini-embedding-001."""
    n = (raw or "").replace("models/", "").strip()
    if not n:
        return "gemini-embedding-001"
    if "text-embedding-004" in n:
        return "gemini-embedding-001"
    return n


def modelo_embedding() -> str:
    raw = (
        os.environ.get("GEMINI_EMBEDDING_MODEL_EX06")
        or os.environ.get("GEMINI_EMBEDDING_MODEL")
        or "gemini-embedding-001"
    )
    return normalize_gemini_embedding_model(raw)


def embed_model() -> GoogleGenAIEmbedding:
    return GoogleGenAIEmbedding(
        model_name=modelo_embedding(),
        api_key=_api_key(),
    )


def llm() -> GoogleGenAI:
    return GoogleGenAI(
        model=modelo_llm(),
        api_key=_api_key(),
        temperature=0.2,
    )


def _cliente_chroma():
    return chromadb.PersistentClient(
        path=str(dir_chroma()),
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def indexar_documentos() -> int:
    """Carrega `data/juridico`, faz chunking/embeddings e grava no Chroma."""
    LISettings.embed_model = embed_model()
    LISettings.llm = llm()

    jur = dir_documentos()
    if not jur.is_dir():
        raise FileNotFoundError(f"Pasta de documentos em falta: {jur}")

    client = _cliente_chroma()
    try:
        client.delete_collection(COLECAO)
    except Exception:
        pass
    col = client.create_collection(COLECAO, metadata={"hnsw:space": "cosine"})
    vector_store = ChromaVectorStore(chroma_collection=col)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    docs = SimpleDirectoryReader(
        input_dir=str(jur),
        required_exts=[".md"],
        recursive=False,
    ).load_data()

    VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        show_progress=True,
    )
    return len(docs)


def obter_index() -> VectorStoreIndex:
    LISettings.embed_model = embed_model()
    LISettings.llm = llm()
    client = _cliente_chroma()
    col = client.get_collection(COLECAO)
    vector_store = ChromaVectorStore(chroma_collection=col)
    return VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=LISettings.embed_model,
    )


def consultar_com_fontes(pergunta: str, top_k: int = 5) -> dict:
    """Resposta sintetizada + trechos e ficheiros mais relevantes (desafio extra)."""
    index = obter_index()
    motor = index.as_query_engine(
        llm=llm(),
        similarity_top_k=top_k,
        response_mode="compact",
    )
    resp = motor.query(pergunta)

    fontes: list[dict] = []
    for node in resp.source_nodes:
        meta = node.metadata or {}
        nome = meta.get("file_name") or meta.get("file_path") or meta.get("filename") or "?"
        if isinstance(nome, str) and "/" in nome:
            nome = Path(nome).name
        fontes.append(
            {
                "score": getattr(node, "score", None),
                "arquivo": nome,
                "trecho": (node.text or "")[:1200],
            }
        )

    def _score_key(f: dict) -> float:
        s = f.get("score")
        return float(s) if isinstance(s, (int, float)) else -1.0

    fontes.sort(key=_score_key, reverse=True)

    return {
        "resposta": str(resp).strip(),
        "fontes": fontes,
    }
