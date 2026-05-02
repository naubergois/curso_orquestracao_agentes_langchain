# Exercício 15 — AuditoriaGraph

## 1. Visão geral

**AuditoriaGraph** classifica achados por **risco** e segue três caminhos: orientação simples, pedido de evidências ou escalonamento humano, gerando **relatório estruturado** (extra).

## 2. Objetivos do exercício

- Implementar **decisão condicional** em LangGraph.
- Integrar **LangSmith** via variáveis de ambiente (rastreio LangChain).

## 3. Frameworks utilizados

- **LangGraph**, **LangChain Google GenAI**, **LangSmith**, **Docker**.

## 4. Arquitetura

```text
Achado → classificar risco ─┬ baixo → orientação
                            ├ médio → evidências
                            └ alto → revisão humana
```

## 5. Estrutura de pastas

- `app/audit_graph.py` — nós e ramos.
- `app/main.py` — `POST /analisar`.

## 6. Como executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

Porta `8015`.

## 7. Variáveis de ambiente

Ver `.env.example`: `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`.

## 8. Explicação do código

Classificação JSON → `add_conditional_edges`; relatório final solicita JSON com causa/consequência/recomendação.

## 9–10. Exemplos

`POST /analisar {"texto": "..."}` → `risco`, `resposta`, `relatorio`, `logs`.

## 11. Critérios de avaliação

Três ramos distintos, observabilidade documentada.

## 12. Possíveis melhorias

Políticas por sector, integração com ticketing, métricas offline.

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
