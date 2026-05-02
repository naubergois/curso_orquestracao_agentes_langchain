# Arquitetura — Exercício 07: Busca Semântica Ltda.

## Visão técnica
Sentence-Transformers (`all-MiniLM-L6-v2`) para embeddings locais → índice FAISS `IndexFlatIP` com vetores L2-normalizados → consulta por similaridade coseno.

## Fluxo
```text
corpus → encode → FAISS.add → query encode → search → top-k + scores
```
