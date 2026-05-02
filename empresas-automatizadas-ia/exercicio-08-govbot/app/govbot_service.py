"""GovBot: indexação + RAG com Haystack (Qdrant + ST embedder + Gemini)."""

from __future__ import annotations

import os
import re
from pathlib import Path

from haystack import Document, Pipeline
from haystack.components.embedders import (
    SentenceTransformersDocumentEmbedder,
    SentenceTransformersTextEmbedder,
)
from haystack.components.writers import DocumentWriter
from haystack.dataclasses.chat_message import ChatMessage
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_EMBED_DIM = 384
_INDEX_NAME = "govbot_cidadao"


def raiz() -> Path:
    return Path(__file__).resolve().parents[1]


def dir_docs() -> Path:
    return raiz() / "data" / "publicos"


def qdrant_url() -> str:
    return os.environ.get("QDRANT_URL", "http://127.0.0.1:6333").strip()


def document_store() -> QdrantDocumentStore:
    return QdrantDocumentStore(
        url=qdrant_url(),
        index=_INDEX_NAME,
        embedding_dim=_EMBED_DIM,
        recreate_index=False,
        return_embedding=False,
        wait_result_from_api=True,
    )


def pipeline_indexacao() -> Pipeline:
    store = document_store()
    pipe = Pipeline()
    pipe.add_component(
        "embedder",
        SentenceTransformersDocumentEmbedder(model=_EMBED_MODEL),
    )
    pipe.add_component("writer", DocumentWriter(document_store=store))
    pipe.connect("embedder.documents", "writer.documents")
    return pipe


def pipeline_consulta() -> Pipeline:
    store = document_store()
    pipe = Pipeline()
    pipe.add_component(
        "text_embedder",
        SentenceTransformersTextEmbedder(model=_EMBED_MODEL),
    )
    pipe.add_component(
        "retriever",
        QdrantEmbeddingRetriever(document_store=store, top_k=5),
    )
    pipe.connect("text_embedder.embedding", "retriever.query_embedding")
    return pipe


def garantir_indice() -> None:
    docs_dir = dir_docs()
    paths = sorted(docs_dir.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"Sem documentos em {docs_dir}")
    docs = [
        Document(content=p.read_text(encoding="utf-8"), meta={"file_name": p.name})
        for p in paths
    ]
    store_probe = QdrantDocumentStore(
        url=qdrant_url(),
        index=_INDEX_NAME,
        embedding_dim=_EMBED_DIM,
        recreate_index=False,
        return_embedding=False,
        wait_result_from_api=True,
    )
    try:
        existentes = store_probe.filter_documents(filters={})
        if existentes:
            return
    except Exception:
        pass

    store = QdrantDocumentStore(
        url=qdrant_url(),
        index=_INDEX_NAME,
        embedding_dim=_EMBED_DIM,
        recreate_index=True,
        return_embedding=False,
        wait_result_from_api=True,
    )
    pipe = Pipeline()
    pipe.add_component(
        "embedder",
        SentenceTransformersDocumentEmbedder(model=_EMBED_MODEL),
    )
    pipe.add_component("writer", DocumentWriter(document_store=store))
    pipe.connect("embedder.documents", "writer.documents")
    pipe.run({"embedder": {"documents": docs}})


def classificar_demanda(texto: str) -> str:
    """Desafio extra — categorização lexical simples."""
    t = texto.lower()
    if any(x in t for x in ("iptu", "imposto predial", "taxa de lixo", "iss")):
        return "imposto"
    if any(x in t for x in ("protocolo", "requerimento", "pedido número", "acompanhar processo")):
        return "protocolo"
    if any(
        x in t
        for x in (
            "iluminação",
            "lâmpada",
            "buraco",
            "via pública",
            "limpeza urbana",
            "coleta",
        )
    ):
        return "servico_urbano"
    if any(x in t for x in ("alvará", "licença", "obra", "regularização")):
        return "licenca"
    return "geral"


def responder(mensagem: str) -> dict:
    garantir_indice()
    modelo = (
        os.environ.get("GEMINI_MODEL_EX08")
        or os.environ.get("GEMINI_MODEL")
        or "gemini-2.0-flash"
    ).replace("models/", "")

    qp = pipeline_consulta()
    emb = qp.run({"text_embedder": {"text": mensagem}})
    docs = emb["retriever"]["documents"]
    contexto = "\n\n".join(
        f"[{d.meta.get('file_name', '?')}]\n{d.content[:1200]}" for d in docs
    )

    gen = GoogleGenAIChatGenerator(model=modelo)
    prompt = (
        "És o GovBot Cidadão de uma autarquia fictícia (PT-PT). "
        "Usa apenas o contexto abaixo. Se não houver dados, diz que não encontraste nos documentos.\n"
        "No final, indica entre parênteses os nomes dos ficheiros que sustentam a resposta.\n\n"
        f"### Contexto\n{contexto}\n\n### Pergunta\n{mensagem}"
    )
    out = gen.run(messages=[ChatMessage.from_user(prompt)])
    texto = out["replies"][0].text if out.get("replies") else "(sem resposta)"

    fontes = [
        {
            "documento": d.meta.get("file_name", "?"),
            "excerto": (d.content or "")[:400],
        }
        for d in docs
    ]
    return {
        "classificacao_demanda": classificar_demanda(mensagem),
        "resposta": texto.strip(),
        "fontes": fontes,
    }
