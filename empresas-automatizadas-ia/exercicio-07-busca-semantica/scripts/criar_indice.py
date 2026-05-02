#!/usr/bin/env python3
"""Cria embeddings (HF Transformers) e índice FAISS a partir de data/documentos/."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from app.embeddings_hf import EmbedderHF, caminho_documentos
from app.faiss_store import gravar_indice


def main() -> None:
    docs_dir = caminho_documentos()
    paths = sorted(docs_dir.glob("*.txt"))
    if not paths:
        raise SystemExit(f"Sem .txt em {docs_dir}")
    textos = [p.read_text(encoding="utf-8") for p in paths]
    nomes = [p.name for p in paths]

    model_id = os.environ.get("HF_EMBEDDING_MODEL", "").strip() or (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    print("Modelo HF:", model_id)
    emb = EmbedderHF(model_id=model_id)
    mat = emb.encode(textos)
    gravar_indice(mat, nomes)
    print(f"Índice FAISS gravado com {len(nomes)} documentos.")


if __name__ == "__main__":
    main()
