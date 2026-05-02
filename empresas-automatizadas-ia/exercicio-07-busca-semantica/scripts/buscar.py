#!/usr/bin/env python3
"""CLI: top 5 documentos semanticamente parecidos com a pergunta."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from app.embeddings_hf import EmbedderHF, caminho_documentos
from app.faiss_store import buscar_semantico, busca_palavra_chave, carregar_indice


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("pergunta", nargs="?", default="Problemas de ligação à rede sem fios no escritório")
    p.add_argument("--keyword", action="store_true", help="Usar só busca lexical (desafio extra)")
    p.add_argument("--comparar", action="store_true", help="Mostrar semântico vs palavra‑chave")
    args = p.parse_args()

    _, nomes = carregar_indice()
    docs_dir = caminho_documentos()
    textos = [(docs_dir / n).read_text(encoding="utf-8") for n in nomes]

    if args.comparar:
        model_id = os.environ.get("HF_EMBEDDING_MODEL", "").strip() or (
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        qv = EmbedderHF(model_id=model_id).encode([args.pergunta])
        sem = buscar_semantico(qv[0], k=5)
        lex = busca_palavra_chave(textos, nomes, args.pergunta, k=5)
        print(json.dumps({"semantico": sem, "palavra_chave": lex}, ensure_ascii=False, indent=2))
        return

    if args.keyword:
        print(json.dumps(busca_palavra_chave(textos, nomes, args.pergunta, k=5), ensure_ascii=False, indent=2))
        return

    model_id = os.environ.get("HF_EMBEDDING_MODEL", "").strip() or (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    qv = EmbedderHF(model_id=model_id).encode([args.pergunta])
    print(json.dumps(buscar_semantico(qv[0], k=5), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
