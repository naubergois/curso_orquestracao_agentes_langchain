# API — RAG Jurídico

Base: `http://127.0.0.1:8000` (mapeamento por defeito em `docker-compose.yml`).

## `GET /health`

Estado do serviço e nomes de modelo configurados.

## `POST /perguntar`

**Corpo JSON**

```json
{
  "pergunta": "Qual é o prazo para resposta contratual segundo o documento?",
  "top_k": 5
}
```

**Resposta `200`**

```json
{
  "resposta": "…",
  "fontes": [
    {
      "score": 0.42,
      "arquivo": "normas_internas_comunicacao.md",
      "trecho": "…"
    }
  ]
}
```

**`503`** — índice em falta (correr `python scripts/indexar.py` dentro do contentor ou no host) ou falha de API.

### Exemplo `curl`

```bash
curl -s -X POST "http://127.0.0.1:8000/perguntar" \
  -H "Content-Type: application/json" \
  -d '{"pergunta":"Qual é o prazo para resposta contratual segundo o documento?","top_k":5}' | jq .
```
