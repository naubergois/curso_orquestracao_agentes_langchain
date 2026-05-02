# Exercício 18 — API Agent Factory

## 1. Visão geral

Fábrica de capacidades expostas como **REST**: chat livre, classificação de intenção e resumo — documentadas em **Swagger**.

## 2. Objetivos do exercício

- Três endpoints **POST** `/chat`, `/classificar`, `/resumir`.
- Esquemas **Pydantic** e **LangChain** com Gemini.
- **Token Bearer opcional** (`API_TOKEN`) — desafio extra.

## 3. Frameworks utilizados

- **FastAPI**, **LangChain**, **Docker**.

## 4. Arquitetura

```text
HTTP JSON → FastAPI → cadeia LCEL (prompt | llm | StrOutputParser) → JSON
```

## 5. Estrutura de pastas

- `app/chains.py` — prompts reutilizáveis.
- `app/main.py` — rotas e dependência de auth.

## 6. Como executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

`http://localhost:8018/docs`

## 7. Variáveis de ambiente

`GOOGLE_API_KEY`, `API_TOKEN` opcional.

## 8. Explicação do código

`_auth` só valida quando `API_TOKEN` está definido; caso contrário os endpoints ficam abertos para desenvolvimento local.

## 9–10. Exemplos (curl)

```bash
curl -X POST http://localhost:8018/resumir \
  -H "Content-Type: application/json" \
  -d '{"texto":"Texto longo..."}'
```

Com token: `-H "Authorization: Bearer <API_TOKEN>"`.

## 11. Critérios de avaliação

OpenAPI legível, erros HTTP claros, Docker.

## 12. Possíveis melhorias

Rate limiting, métricas Prometheus, versões de modelo por cabeçalho.

## 13. Testes automatizados

Os testes do monorepo vivem na raiz [`empresas-automatizadas-ia/tests/`](../tests/) e validam sobretudo **`GET /health`** desta API (quando existe FastAPI em `app/main.py`).

```bash
cd ..    # raiz `empresas-automatizadas-ia/` (pasta que contém `tests/` e `scripts/`)
pip install -r requirements-dev.txt
./scripts/install_test_deps.sh   # ou apenas: pip install -r requirements.txt (nesta pasta)
pytest tests -m "not integration"
```

- **Integração** (Gemini real): `pytest tests -m integration` — requer `GOOGLE_API_KEY`.

Guia completo: [`docs/GUIA_TESTES.md`](../docs/GUIA_TESTES.md).

### Troubleshooting

| Sintoma | O que verificar |
|--------|------------------|
| `ModuleNotFoundError` | Instalar o `requirements.txt` **desta** pasta; para a suíte inteira usar `./scripts/install_test_deps.sh`. |
| Conflitos de versão entre empresas | Usar um **venv por exercício** ou correr testes dentro do **Dockerfile** desse exercício. |
| Ex. 07 — `/buscar` falha | Criar o índice FAISS com `scripts/criar_indice.py` antes de testes que chamem `/buscar`. |
| Ex. 09 / LangGraph | Manter `langgraph>=0.2,<0.3` com `langchain-core` 0.3.x (ver `GUIA_TESTES.md`). |
