# Exercício 19 — resumo de chat por utilizador (PostgreSQL)

- **Objectivo:** guardar um **resumo acumulado** por `external_id` de utilizador; em cada **nova sessão** de chat, injectar esse texto como contexto (mensagem de sistema).
- **Stack:** LangGraph `create_react_agent` + `MemorySaver` (histórico da sessão actual), **Gemini**, **PostgreSQL** (`init_db/01_schema.sql`).
- **Arranque:** `./run.sh` ou `.\run.ps1` — Jupyter sem token; Postgres no host na porta **`POSTGRES_PORT`** (predefinição **5437**).

Variáveis: **`GOOGLE_API_KEY`** (ou `GEMINI_API_KEY`); opcional **`GEMINI_MODEL_EX19`**. No contentor, `DATABASE_URL` vem do compose; fora do Docker, use `postgresql://curso:curso@127.0.0.1:5437/chat_memoria_demo` se não definir `DATABASE_URL`.
