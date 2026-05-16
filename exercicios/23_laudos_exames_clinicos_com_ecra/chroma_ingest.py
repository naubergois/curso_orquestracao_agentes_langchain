"""Indexação Chroma: laudos (Postgres) + textos pedagógicos fictícios."""

from __future__ import annotations

import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import db_laudos

COLLECTION = "laudos_clinicos_demo"


def _persist_dir() -> str:
    return (os.environ.get("CHROMA_PERSIST_DIR") or str(Path(__file__).resolve().parent / "chroma_data")).strip()


def _embeddings() -> GoogleGenerativeAIEmbeddings:
    modelo = (
        os.environ.get("GEMINI_EMBEDDING_MODEL")
        or os.environ.get("GEMINI_EMBEDDING_MODEL_004")
        or "gemini-embedding-001"
    ).strip()
    if modelo.startswith("models/"):
        modelo = modelo.removeprefix("models/")
    legacy = {"text-embedding-004", "embedding-001"}
    if modelo in legacy:
        modelo = "gemini-embedding-001"
    return GoogleGenerativeAIEmbeddings(model=modelo)


def _documentos_pedagogicos() -> list[Document]:
    textos = [
        (
            "troponina",
            "Elevação de troponina de alta sensibilidade com curva dinâmica sugere lesão miocárdica; "
            "correlacionar com sintomas, ECG e factores de risco cardiovascular. Em formação, simular discussão "
            "de regra-in / regra-out de SCA.",
        ),
        (
            "hipercalemia",
            "Hipercalemia moderada a grave pode associar-se a alterações de condução e risco arritmico. "
            "Rever medicamentos (IECA, ARA, diuréticos poupadores de potássio), função renal e acidose.",
        ),
        (
            "drc_anemia",
            "Anemia em doente com DRC pode ser multifactorial (deficiência de ferro, eritropoietina, "
            "toxicidade medicamentosa). Integrar com ferro serico, ferritina e hemograma previo.",
        ),
        (
            "leucocitose",
            "Leucocitose com desvio esquerdo pode indicar infecção bacteriana, mas também stress, "
            "corticoterapia ou leucemias. Contexto clínico e imagiologia orientam a urgência.",
        ),
        (
            "tireoide",
            "TSH suprimido com T4 livre elevado sugere hipertireoidismo; TSH suprimido com T4 normal pode "
            "ser subclínico — decisão terapêutica depende de sintomas, idade e comorbilidades.",
        ),
    ]
    return [
        Document(page_content=t, metadata={"fonte": "protocolo_pedagogico", "tema": tag})
        for tag, t in textos
    ]


def garantir_indice_chroma(*, reconstruir: bool = False) -> Chroma:
    """Carrega ou cria a coleção Chroma com laudos + protocolos demo."""
    persist = _persist_dir()
    Path(persist).mkdir(parents=True, exist_ok=True)
    emb = _embeddings()

    if not reconstruir:
        try:
            vs = Chroma(
                collection_name=COLLECTION,
                embedding_function=emb,
                persist_directory=persist,
            )
            if vs._collection.count() > 0:
                return vs
        except Exception:
            pass

    import chromadb

    client = chromadb.PersistentClient(path=persist)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass

    docs: list[Document] = []
    docs.extend(_documentos_pedagogicos())
    for p in db_laudos.listar_pacientes_resumo():
        pid = int(p["id"])
        corpo = db_laudos.laudos_paciente_texto(pid)
        if corpo and corpo != "(sem exames)":
            docs.append(
                Document(
                    page_content=f"Paciente ID {pid} — {p['nome_completo']}, {p['idade']} anos.\n\n{corpo}",
                    metadata={"paciente_id": str(pid), "fonte": "laudo_postgres"},
                )
            )

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    if not chunks:
        raise RuntimeError("Sem documentos para indexar.")
    return Chroma.from_documents(
        documents=chunks,
        embedding=emb,
        collection_name=COLLECTION,
        persist_directory=persist,
    )


def as_retriever(k: int = 6):
    vs = garantir_indice_chroma(reconstruir=False)
    return vs.as_retriever(search_kwargs={"k": k})
