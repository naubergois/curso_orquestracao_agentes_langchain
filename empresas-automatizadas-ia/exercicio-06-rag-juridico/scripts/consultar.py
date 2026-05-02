#!/usr/bin/env python3
"""Consulta semântica: pergunta → retriever Chroma → resposta + fontes (trechos)."""

from __future__ import annotations

import argparse
import json
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

from app.rag.pipeline import consultar_com_fontes


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG Jurídico — consulta com fontes")
    parser.add_argument(
        "pergunta",
        nargs="?",
        default="Qual é o prazo para resposta contratual segundo o documento?",
        help="Pergunta em linguagem natural",
    )
    parser.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=5,
        help="Número de nós a recuperar (predefinição: 5)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprime só JSON (stdout)",
    )
    args = parser.parse_args()

    out = consultar_com_fontes(args.pergunta, top_k=args.top_k)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    print("--- Resposta ---\n")
    print(out["resposta"])
    print("\n--- Documentos / trechos mais relevantes ---\n")
    for i, f in enumerate(out["fontes"], 1):
        sc = f.get("score")
        sc_s = f"{sc:.4f}" if isinstance(sc, float) else str(sc)
        print(f"[{i}] ficheiro={f['arquivo']}  score={sc_s}")
        print(f"{f['trecho']}\n{'-' * 60}\n")


if __name__ == "__main__":
    main()
