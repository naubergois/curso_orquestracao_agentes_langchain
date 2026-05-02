# Passo a passo — Exercício 5: Parser Jurídico

## 1. Ambiente

1. Na **raiz do repositório do curso**, crie `.env` com `GOOGLE_API_KEY` (ou `GEMINI_API_KEY`, conforme o resto do curso).
2. Opcional: `GEMINI_MODEL_EX05=gemini-2.0-flash` (senão usa `GEMINI_MODEL`).

## 2. API (entrega principal)

```bash
cd empresas-automatizadas-ia/exercicio-05-parser-juridico
./run_api.sh
```

1. Abra `http://127.0.0.1:8000/docs`.
2. Experimente `POST /analisar` com um texto longo (≥ 40 caracteres) claramente **jurídico** e outro claramente **não jurídico** (ex.: receita) — o segundo deve devolver `422` com `TEXTO_NAO_JURIDICO`.
3. Exemplos `curl` em [`docs/API.md`](API.md).

## 3. Jupyter (opcional)

```bash
./run.sh
```

Execute `exercicio_05_sem_ecra.ipynb` se quiser percorrer o tema de forma didática; a implementação de referência da API está em `app/`.

## 4. Parar containers

```bash
docker compose down
docker compose -f docker-compose.jupyter.yml down
```
