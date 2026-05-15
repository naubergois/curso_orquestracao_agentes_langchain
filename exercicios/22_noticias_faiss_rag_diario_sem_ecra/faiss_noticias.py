"""Pesquisa Web (DuckDuckGo) + indexação FAISS para notícias do dia."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for d in (here.parent, *here.parents):
        env = d / ".env"
        if env.is_file():
            load_dotenv(env, override=False)
            return


_load_local_env()

# Último texto bruto da pesquisa (o agente de recolha preenche; o de indexação lê).
_ultima_pesquisa_bruta: str = ""
_ultima_consulta: str = ""


def ultima_pesquisa_snapshot() -> tuple[str, str]:
    return _ultima_consulta, _ultima_pesquisa_bruta


def definir_ultima_pesquisa(consulta: str, texto_bruto: str) -> None:
    global _ultima_pesquisa_bruta, _ultima_consulta
    _ultima_consulta = (consulta or "").strip()
    _ultima_pesquisa_bruta = texto_bruto or ""


def _garantir_chave_google() -> None:
    k = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not k:
        raise RuntimeError("Defina GOOGLE_API_KEY ou GEMINI_API_KEY para embeddings Gemini (FAISS).")
    os.environ.setdefault("GOOGLE_API_KEY", k)


def _norm_embedding_model(nome: str) -> str:
    """Normaliza o nome e mapeia identificadores antigos (404 em v1beta com embedContent)."""
    n = (nome or "").strip()
    if n.startswith("models/"):
        n = n.removeprefix("models/")
    legacy = {
        "text-embedding-004",
        "text-embedding-004-embedding-preview",
        "embedding-001",
    }
    if n in legacy:
        return "gemini-embedding-001"
    return n or "gemini-embedding-001"


def embeddings_gemini() -> GoogleGenerativeAIEmbeddings:
    _garantir_chave_google()
    raw = (
        os.environ.get("GEMINI_EMBEDDING_MODEL")
        or os.environ.get("GEMINI_EMBEDDING_MODEL_004")
        or "gemini-embedding-001"
    ).strip()
    modelo = _norm_embedding_model(raw)
    return GoogleGenerativeAIEmbeddings(model=modelo)


def pesquisa_duckduckgo_texto(consulta: str, *, max_resultados: int = 12) -> str:
    """Invoca DuckDuckGo (langchain_community). Requer rede."""
    from langchain_community.tools import DuckDuckGoSearchResults

    q = (consulta or "").strip()
    if not q:
        raise ValueError("consulta vazia.")
    search = DuckDuckGoSearchResults(max_results=max(1, min(max_resultados, 20)))
    try:
        raw = search.invoke(q)
    except Exception:
        raw = search.invoke({"query": q})
    texto = raw if isinstance(raw, str) else str(raw)
    definir_ultima_pesquisa(q, texto)
    return texto


def _fragmentos_para_documentos(texto: str, consulta: str) -> list[Document]:
    """Parte o resultado DDG em blocos (URLs/manchetes) quando possível; senão um único documento."""
    texto = (texto or "").strip()
    if not texto:
        return []
    partes = re.split(r"\n{2,}", texto)
    docs: list[Document] = []
    for i, bloco in enumerate(partes):
        b = bloco.strip()
        if len(b) < 40:
            continue
        docs.append(
            Document(
                page_content=b[:12000],
                metadata={"consulta": consulta, "bloco": i, "fonte": "duckduckgo"},
            )
        )
    if not docs:
        docs.append(
            Document(
                page_content=texto[:50000],
                metadata={"consulta": consulta, "fonte": "duckduckgo"},
            )
        )
    return docs


def dividir_documentos(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    return splitter.split_documents(docs)


def caminho_indice_padrao() -> Path:
    return Path(__file__).resolve().parent / "faiss_noticias_index"


def indexar_ultima_pesquisa_em_faiss(
    persist_directory: Path | None = None,
    *,
    substituir: bool = True,
) -> int:
    """Indexa `_ultima_pesquisa_bruta` em FAISS. Devolve número de chunks."""
    consulta, bruto = ultima_pesquisa_snapshot()
    if not bruto.strip():
        raise RuntimeError(
            "Não há pesquisa recente em memória. Chame primeiro a tool de pesquisa Web (ou `pesquisa_duckduckgo_texto`)."
        )
    persist_directory = persist_directory or caminho_indice_padrao()
    persist_directory = Path(persist_directory)
    persist_directory.mkdir(parents=True, exist_ok=True)

    docs = _fragmentos_para_documentos(bruto, consulta)
    chunks = dividir_documentos(docs)
    if not chunks:
        raise RuntimeError("Nenhum chunk gerado a partir da pesquisa.")
    emb = embeddings_gemini()
    if substituir and persist_directory.exists():
        import shutil

        for child in list(persist_directory.iterdir()):
            if child.is_file():
                try:
                    child.unlink(missing_ok=True)
                except OSError:
                    pass
            elif child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
    vs = FAISS.from_documents(chunks, emb)
    vs.save_local(str(persist_directory))
    return len(chunks)


def carregar_faiss(persist_directory: Path | None = None) -> FAISS:
    persist_directory = Path(persist_directory or caminho_indice_padrao())
    if not persist_directory.is_dir() or not any(persist_directory.iterdir()):
        raise RuntimeError(
            f"Índice FAISS inexistente em `{persist_directory}`. "
            "Execute primeiro o agente de recolha (pesquisa + indexação)."
        )
    return FAISS.load_local(
        str(persist_directory),
        embeddings_gemini(),
        allow_dangerous_deserialization=True,
    )


def retriever_noticias(k: int = 6, persist_directory: Path | None = None) -> Any:
    vs = carregar_faiss(persist_directory)
    return vs.as_retriever(search_kwargs={"k": k})
