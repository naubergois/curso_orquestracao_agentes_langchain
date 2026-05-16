# Exercício 23 — laudos laboratoriais fictícios (Streamlit)

Cenário **pedagógico**: 10 pacientes em **PostgreSQL** com laudos de texto; **ChromaDB** indexa laudos + mini-protocolos fictícios; **LangGraph** grava avaliações de gravidade (saída **Pydantic**) na tabela `avaliacoes_engine`; **agente ReAct** (LangGraph + Gemini) permite ao «médico» conversar com *tools* SQL + RAG.

## Requisitos

- `.env` na raiz com **`GOOGLE_API_KEY`** (ou `GEMINI_API_KEY`).
- **Docker** (recomendado): Postgres + Streamlit + volume Chroma.

## Arranque

```bash
cd exercicios/23_laudos_exames_clinicos_com_ecra
./run.sh
```

Interface: **http://localhost:8511** (ou `STREAMLIT_PORT`).

Local (venv na raiz do repo, Postgres exposto no host):

```bash
POSTGRES_PORT_EX23=5441 ./run.sh --local
```

## Variáveis úteis

| Variável | Descrição |
|----------|-----------|
| `GEMINI_MODEL_EX23` | Modelo Gemini para chat e avaliação (senão `GEMINI_MODEL`). |
| `GEMINI_EMBEDDING_MODEL` | Embeddings Chroma (senão `gemini-embedding-001`). |
| `POSTGRES_PORT_EX23` | Porta host→5432 no Docker (predef.: **5441**). |
| `STREAMLIT_PORT` | Porta Streamlit (predef.: **8511**). |

## Aviso legal / clínico

Todos os dados são **fictícios**. O sistema **não** fornece diagnóstico nem conduta clínica real.
