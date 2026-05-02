"""Índice FAISS + metadados (nomes dos ficheiros)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import faiss
import numpy as np

from app.embeddings_hf import caminho_indices


def _tokens(s: str) -> set[str]:
    return {t for t in re.findall(r"\w+", s.lower()) if len(t) > 2}


def busca_palavra_chave(textos: list[str], nomes: list[str], consulta: str, k: int = 5) -> list[dict]:
    """Baseline lexical: contagem de tokens da consulta presentes em cada documento."""
    qset = _tokens(consulta)
    if not qset:
        return []
    scored: list[tuple[int, str]] = []
    for nome, txt in zip(nomes, textos):
        tset = _tokens(txt)
        score = sum(1 for w in qset if w in tset)
        if score > 0:
            scored.append((score, nome))
    scored.sort(key=lambda x: -x[0])
    max_s = scored[0][0] if scored else 1
    return [
        {"documento": nome, "score": round(min(1.0, s / max_s), 4)}
        for s, nome in scored[:k]
    ]


def gravar_indice(vectors: np.ndarray, nomes: list[str]) -> None:
    base = caminho_indices()
    base.mkdir(parents=True, exist_ok=True)
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)
    faiss.write_index(index, str(base / "faiss_ip.index"))
    (base / "documentos.json").write_text(json.dumps(nomes, ensure_ascii=False, indent=2), encoding="utf-8")


def carregar_indice() -> tuple[faiss.Index, list[str]]:
    base = caminho_indices()
    idx_path = base / "faiss_ip.index"
    meta_path = base / "documentos.json"
    if not idx_path.is_file() or not meta_path.is_file():
        raise FileNotFoundError(
            "Índice em falta. Execute: python scripts/criar_indice.py"
        )
    index = faiss.read_index(str(idx_path))
    nomes = json.loads(meta_path.read_text(encoding="utf-8"))
    return index, nomes


def buscar_semantico(pergunta_vec: np.ndarray, k: int = 5) -> list[dict]:
    """Inner product com vectores L2-normalizados ≈ similaridade de coseno."""
    index, nomes = carregar_indice()
    q = pergunta_vec.astype("float32").reshape(1, -1)
    scores, ids = index.search(q, min(k, index.ntotal))
    resultados: list[dict] = []
    for sc, i in zip(scores[0], ids[0]):
        if i < 0:
            continue
        resultados.append({"documento": nomes[i], "score": round(float(sc), 4)})
    return resultados


def carregar_textos_originais(caminho_docs: Path, nomes: list[str]) -> list[str]:
    return [(caminho_docs / n).read_text(encoding="utf-8") for n in nomes]
