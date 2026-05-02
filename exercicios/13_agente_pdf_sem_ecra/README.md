# Exercício 13 — agente sobre texto de PDFs *chunkado* (sem ecrã)

Gera PDFs fictícios, extrai texto, divide em **chunks** e expõe **ferramentas** LangChain para um **agente ReAct** (LangGraph + **Gemini**) explorar o corpus antes de responder.

Requisito: **`GOOGLE_API_KEY`** no `.env` na raiz do repositório.

## Arranque

```bash
./run.sh
```

Abrir `exercicio_13_sem_ecra.ipynb`. Modelo opcional: **`GEMINI_MODEL_EX13`**; senão **`GEMINI_MODEL`**.

Ver também o **exercício 12** (só PDF + splits, sem agente).
