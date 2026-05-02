# Passo a passo — Exercício 03: EduPrompt Academy

## 1. Ambiente

1. Configure `GOOGLE_API_KEY` no `.env` na **raiz do repositório do curso**.
2. Na pasta `exercicio-03-eduprompt`, execute `./run.sh` para abrir Jupyter Lab.

## 2. Notebook

1. Abra [`exercicio_03_sem_ecra.ipynb`](../exercicio_03_sem_ecra.ipynb).
2. Execute as células **na ordem** — todo o LangChain/LCEL está **no próprio notebook** (texto explicativo + código).
3. Confirme que a entrada `{"tema": "RAG", "nivel": "iniciante"}` produz Markdown com `## Explicação`, `## Exercícios`, `## Resumo`.

## 3. Código modular (opcional)

Para comparar com o que digitou no Jupyter: [`app/chains/eduprompt_chains.py`](../app/chains/eduprompt_chains.py) e [`docs/chains.md`](chains.md).

## 4. API Docker (opcional)

```bash
./run_api.sh
```

Teste:

```bash
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/eduprompt/pacote \
  -H "Content-Type: application/json" \
  -d '{"tema":"RAG","nivel":"iniciante"}'
```

## 5. Parar containers

```bash
docker compose -f docker-compose.jupyter.yml down
docker compose down
```
