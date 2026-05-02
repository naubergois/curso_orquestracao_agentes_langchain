#!/usr/bin/env python3
"""Indexação: `data/juridico` → chunks → embeddings → ChromaDB (LlamaIndex)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from dotenv import load_dotenv

_REPO = ROOT.parent.parent
load_dotenv(_REPO / ".env", override=False)
load_dotenv(ROOT / ".env", override=True)

from app.rag.pipeline import indexar_documentos


def main() -> None:
    n = indexar_documentos()
    print(f"Concluído: {n} documentos indexados em data/chroma_juridico/")


if __name__ == "__main__":
    main()
