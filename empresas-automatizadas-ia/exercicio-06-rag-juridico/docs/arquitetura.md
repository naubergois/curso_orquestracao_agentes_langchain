# Arquitetura — Exercício 06: RAG Jurídico

## Visão técnica
Fragmentação de documentos fictícios → embeddings (Gemini) → vetor em memória (Chroma) → retriever → prompt com contexto → resposta fundamentada.

## Componentes
- **Loader:** strings/ficheiros em `app/data/`.
- **Vector store:** Chroma persistente em disco opcional; aqui uso em memória para notebook.
