# API — Parser Jurídico (Exercício 5)

Base URL local (Docker): `http://127.0.0.1:8000`

## `GET /health`

Estado do serviço e modelo configurado.

## `POST /analisar`

**Corpo JSON**

| Campo | Tipo | Notas |
|-------|------|--------|
| `texto` | string | Mínimo **40** caracteres |

**Resposta `200`** — schema `DemandaExtraida` (ver OpenAPI `/docs`).

**Resposta `422`** — texto não jurídico (bloqueio):

```json
{
  "detail": {
    "codigo": "TEXTO_NAO_JURIDICO",
    "mensagem": "…"
  }
}
```

Ou falha de validação do body FastAPI (`texto` curto).

**Resposta `503`** — `GOOGLE_API_KEY` em falta ou erro ao invocar o modelo.

### Exemplo — texto jurídico

```bash
curl -s -X POST "http://127.0.0.1:8000/analisar" \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "Exmo. Sr. Advogado, sou cliente da empresa Alfa desde 2022. Em março de 2025 deixámos de receber as mercadorias contratadas apesar do pagamento da segunda prestação. Solicitámos esclarecimentos por escrito e deram-nos um prazo de quinze dias que já expirou. Pedimos orientação sobre incumprimento contratual e eventuais indemnizações."
  }' | jq .
```

### Exemplo — texto não jurídico (deve falhar com `422`)

```bash
curl -s -X POST "http://127.0.0.1:8000/analisar" \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "Para fazer um bolo de chocolate precisa de farinha, açúcar, ovos e manteiga. Misture tudo e leve ao forno durante trinta minutos. Sirva com cobertura a gosto. Esta receita rende oito porções generosas para a família."
  }' | jq .
```
