# Exercício 16 — ObservaAI

## 1. Visão geral

**ObservaAI** executa **três prompts** distintos sobre a mesma entrada e regista latência, erro, custo estimado e avaliação manual opcional, com **MLflow** local e **dashboard Streamlit** (extra).

## 2. Objetivos do exercício

- Comparar comportamentos de prompts em ambiente controlado.
- Persistir traços em **MLflow** (`file:./data/mlruns`) e **JSONL** para UI simples.

## 3. Frameworks utilizados

- **LangChain Google GenAI**, **MLflow**, **LangSmith (opcional)**, **Streamlit**, **Docker Compose**.

## 4. Arquitetura

```text
entrada → três chamadas Gemini → métricas → MLflow + runs.jsonl → Streamlit
```

## 5. Estrutura de pastas

- `app/experimentos.py` — loops de prompts e logging.
- `streamlit_app.py` — painel de leitura dos runs.

## 6. Como executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

- API: `http://localhost:8016`
- Dashboard: `http://localhost:8516`

## 7. Variáveis de ambiente

`GOOGLE_API_KEY`, chaves LangSmith opcionais.

## 8. Explicação do código

Cada prompt escreve um run MLflow com texto de entrada/saída; falhas capturadas sem abortar o lote.

## 9–10. Exemplos

`POST /experimentos {"entrada":"...", "avaliacao_manual":"4/5"}`.

## 11. Critérios de avaliação

Registo completo (tempo, erro, custo estimado), comparabilidade entre prompts.

## 12. Possíveis melhorias

Weights & Biases, custos reais por billing API, testes A/B agendados.

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
