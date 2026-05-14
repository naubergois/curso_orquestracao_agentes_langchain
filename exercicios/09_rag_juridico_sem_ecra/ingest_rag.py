"""Ingestão em ChromaDB com **vários tipos de embeddings** (Gemini API + FastEmbed ONNX).

Coleções por defeito:
  - `juridico_fastembed_local` — `FastEmbedEmbeddings` (multilingual MiniLM ONNX, local; **sem** chave Google)
  - `juridico_gemini_001` — `GoogleGenerativeAIEmbeddings` (`gemini-embedding-001`)
  - `juridico_gemini_2` — `GoogleGenerativeAIEmbeddings` (`gemini-embedding-2-preview`; **espaço de embeddings distinto** do 001)

Variáveis úteis: `FASTEMBED_MODEL`, `FASTEMBED_CACHE_DIR` (se vazio, usa `09_rag_juridico_sem_ecra/.fastembed_cache` em disco),
`GEMINI_EMBEDDING_MODEL`, `GEMINI_EMBEDDING_MODEL_ALT`,
`GEMINI_EMBEDDING_2_OUTPUT_DIMENSIONALITY`, `GEMINI_EMBEDDING_2_BATCH_SIZE` (ver `.env.example`).

Uso na pasta do exercício:
  python ingest_rag.py
"""

from __future__ import annotations

import os
import shutil
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal

# Antes de importar chromadb/langchain_chroma (telemetria PostHog vs. chromadb).
os.environ.setdefault("ANONYMIZED_TELEMETRY", "false")
os.environ.setdefault("CHROMADB_ANONYMIZED_TELEMETRY", "false")

from dotenv import load_dotenv
from langchain_chroma import Chroma

if TYPE_CHECKING:
    from chromadb.config import Settings
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for d in (here.parent, *here.parents):
        env = d / ".env"
        if env.is_file():
            load_dotenv(env, override=False)
            return


def _chroma_client_settings() -> "Settings":
    from chromadb.config import Settings

    return Settings(anonymized_telemetry=False)


class _GeminiAltEmbeddings:
    """Modelo Gemini «alternativo» com lotes mais pequenos e textos nunca vazios.

    Em alguns ambientes, ``gemini-embedding-2-*`` com lotes grandes devolve
    respostas onde a lista de embeddings não corresponde aos textos, o que
    provoca ``list index out of range`` ao indexar no Chroma.
    """

    def __init__(self, inner: GoogleGenerativeAIEmbeddings, *, batch_size: int) -> None:
        self._inner = inner
        self._batch_size = batch_size

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        safe = [t if (t or "").strip() else " " for t in texts]
        return self._inner.embed_documents(safe, batch_size=self._batch_size)

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        safe = [t if (t or "").strip() else " " for t in texts]
        return await self._inner.aembed_documents(safe, batch_size=self._batch_size)

    def embed_query(self, text: str) -> list[float]:
        t = text if (text or "").strip() else " "
        return self._inner.embed_query(t)

    async def aembed_query(self, text: str) -> list[float]:
        t = text if (text or "").strip() else " "
        return await self._inner.aembed_query(t)


def _gemini2_optional_output_dim(model: str) -> int | None:
    if "gemini-embedding-2" not in model:
        return None
    raw = (os.environ.get("GEMINI_EMBEDDING_2_OUTPUT_DIMENSIONALITY") or "768").strip()
    if not raw or raw.lower() in ("none", "default", "0"):
        return None
    return int(raw)


def _gemini2_batch_size() -> int:
    raw = (os.environ.get("GEMINI_EMBEDDING_2_BATCH_SIZE") or "16").strip()
    try:
        b = int(raw)
    except ValueError:
        b = 16
    return max(1, min(b, 100))


def _garantir_chave() -> None:
    k = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not k:
        raise RuntimeError("Defina GOOGLE_API_KEY ou GEMINI_API_KEY para embeddings Gemini.")
    os.environ.setdefault("GOOGLE_API_KEY", k)


def _norm_gemini_model(name: str) -> str:
    n = (name or "").strip()
    if n.startswith("models/"):
        n = n[len("models/") :]
    return n


def _gemini_embedding_primary() -> str:
    raw = (
        os.environ.get("GEMINI_EMBEDDING_MODEL")
        or os.environ.get("GEMINI_EMBEDDING_MODEL_004")
        or "gemini-embedding-001"
    ).strip()
    raw = _norm_gemini_model(raw)
    # Nomes antigos da API (404 em v1beta com embedContent actual)
    if raw in ("text-embedding-004", "embedding-001", "text-embedding-004-embedding-preview"):
        return "gemini-embedding-001"
    return raw


def _gemini_embedding_alt() -> str:
    raw = (
        os.environ.get("GEMINI_EMBEDDING_MODEL_ALT")
        or os.environ.get("GEMINI_EMBEDDING_MODEL_LEGACY")
        or "gemini-embedding-2-preview"
    ).strip()
    raw = _norm_gemini_model(raw)
    if raw in ("embedding-001", "text-embedding-004"):
        return "gemini-embedding-2-preview"
    return raw


def carregar_pdfs_como_documentos(pdf_paths: list[Path]) -> list[Document]:
    docs: list[Document] = []
    for p in pdf_paths:
        reader = PdfReader(str(p))
        parts: list[str] = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
        body = "\n\n".join(parts).strip()
        if body:
            docs.append(
                Document(
                    page_content=body,
                    metadata={"source": p.name, "path": str(p)},
                )
            )
    return docs


def dividir_documentos(
    docs: list[Document],
    *,
    chunk_size: int = 900,
    chunk_overlap: int = 120,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
    )
    return splitter.split_documents(docs)


def _build_embeddings_gemini_primary() -> GoogleGenerativeAIEmbeddings:
    _garantir_chave()
    return GoogleGenerativeAIEmbeddings(model=_gemini_embedding_primary())


def _build_embeddings_gemini_alt() -> GoogleGenerativeAIEmbeddings | _GeminiAltEmbeddings:
    _garantir_chave()
    model = _gemini_embedding_alt()
    dim = _gemini2_optional_output_dim(model)
    kwargs: dict = {"model": model}
    if dim is not None:
        kwargs["output_dimensionality"] = dim
    inner = GoogleGenerativeAIEmbeddings(**kwargs)
    return _GeminiAltEmbeddings(inner, batch_size=_gemini2_batch_size())


def _build_embeddings_fastembed() -> FastEmbedEmbeddings:
    name = (
        os.environ.get("FASTEMBED_MODEL")
        or "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ).strip()
    # Cache estável por defeito (evita ONNX em `/var/folders/.../T/` incompleto ou apagado pelo SO).
    cache = (os.environ.get("FASTEMBED_CACHE_DIR") or "").strip()
    if not cache:
        cache = str(Path(__file__).resolve().parent / ".fastembed_cache")
    Path(cache).mkdir(parents=True, exist_ok=True)
    return FastEmbedEmbeddings(model_name=name, cache_dir=cache)


def limpar_dados_chroma(persist_directory: Path) -> None:
    """Remove coleções e ficheiros Chroma **sem** apagar a pasta raiz.

    Em Docker, `chroma_juridico` costuma ser um *volume* montado em `/app/sem_ecra/chroma_juridico`;
    `shutil.rmtree` nessa raiz provoca ``OSError: [Errno 16] Device or resource busy``.
    """
    persist_directory = Path(persist_directory)
    if not persist_directory.exists():
        return

    try:
        import chromadb
        from chromadb.config import Settings

        client = chromadb.PersistentClient(
            path=str(persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )
        for col in client.list_collections():
            try:
                client.delete_collection(col.name)
            except Exception:
                pass
    except Exception:
        pass

    try:
        for child in list(persist_directory.iterdir()):
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                try:
                    child.unlink(missing_ok=True)
                except OSError:
                    pass
    except OSError:
        pass


def listar_factories_embeddings() -> dict[str, Callable[[], Any]]:
    """Embeddings disponíveis para indexar (cada um → uma coleção Chroma)."""

    def fastembed_local() -> FastEmbedEmbeddings:
        return _build_embeddings_fastembed()

    def gemini_001() -> GoogleGenerativeAIEmbeddings:
        return _build_embeddings_gemini_primary()

    def gemini_2() -> GoogleGenerativeAIEmbeddings | _GeminiAltEmbeddings:
        return _build_embeddings_gemini_alt()

    return {
        "juridico_fastembed_local": fastembed_local,
        "juridico_gemini_001": gemini_001,
        "juridico_gemini_2": gemini_2,
    }


def indexar_embeddings(
    chunks: list[Document],
    persist_directory: Path,
    *,
    limpar: bool = False,
) -> list[str]:
    """Cria ou substitui uma coleção por tipo de embedding. Devolve nomes das coleções escritas."""
    persist_directory = Path(persist_directory)
    persist_directory.mkdir(parents=True, exist_ok=True)

    factories = listar_factories_embeddings()
    if limpar and persist_directory.exists():
        limpar_dados_chroma(persist_directory)

    criadas: list[str] = []
    for collection_name, factory in factories.items():
        try:
            emb = factory()
            Chroma.from_documents(
                documents=chunks,
                embedding=emb,
                persist_directory=str(persist_directory),
                collection_name=collection_name,
                client_settings=_chroma_client_settings(),
            )
            criadas.append(collection_name)
            print(
                f"[ingest] Coleção `{collection_name}` com {len(chunks)} chunks.",
                flush=True,
            )
        except Exception as e:
            print(
                f"[ingest] Aviso: não foi possível indexar `{collection_name}` — {e!s}",
                flush=True,
            )
    return criadas


def carregar_vectorstore(
    collection_name: str,
    persist_directory: Path,
) -> Chroma:
    """Abre uma coleção existente (usa o mesmo tipo de embedding da ingestão)."""
    factories = listar_factories_embeddings()
    if collection_name not in factories:
        raise ValueError(
            f"Coleção desconhecida: {collection_name}. Opções: {list(factories)}"
        )
    emb = factories[collection_name]()
    persist_directory = Path(persist_directory)
    try:
        vs = Chroma(
            collection_name=collection_name,
            embedding_function=emb,
            persist_directory=str(persist_directory),
            client_settings=_chroma_client_settings(),
        )
        # Força leitura do sysdb; pastas antigas / corruptas falham aqui com nitidez.
        vs.similarity_search("__chroma_sanity__", k=1)
    except sqlite3.OperationalError as e:
        raise RuntimeError(
            f"Chroma em `{persist_directory}` parece vazio, corrupto, só leitura ou incompatível com esta versão "
            "do chromadb (por exemplo esquema SQLite antigo). Corrija permissões, apague essa pasta ou execute a "
            "ingestão com `limpar_chroma=True` e volte a indexar."
        ) from e
    return vs


def pipeline_completo(
    diretorio_pdfs: Path | None = None,
    persist_directory: Path | None = None,
    *,
    limpar_chroma: bool = False,
    fonte_pdfs: Literal["estatico", "agente"] = "estatico",
) -> tuple[list[Path], list[str]]:
    _load_local_env()
    here = Path(__file__).resolve().parent
    diretorio_pdfs = diretorio_pdfs or (here / "pdf_fontes")
    persist_directory = persist_directory or (here / "chroma_juridico")

    if fonte_pdfs == "agente":
        from agent_gerador_pdfs import executar_geracao_pdfs_via_agente

        pdfs = executar_geracao_pdfs_via_agente(diretorio_pdfs)
    else:
        from gerar_pdfs_conceitos import gerar_todos_pdfs

        pdfs = gerar_todos_pdfs(diretorio_pdfs)

    docs = carregar_pdfs_como_documentos(pdfs)
    if not docs:
        raise RuntimeError("Nenhum texto extraído dos PDFs.")
    chunks = dividir_documentos(docs)
    chunks = [c for c in chunks if (c.page_content or "").strip()]
    if not chunks:
        raise RuntimeError("Sem chunks de texto não vazios para indexar.")
    nomes = indexar_embeddings(
        chunks, persist_directory, limpar=limpar_chroma
    )
    return pdfs, nomes


if __name__ == "__main__":
    _load_local_env()
    pipeline_completo(limpar_chroma=True)
