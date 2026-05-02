# Exercício 07 — Busca Semântica Ltda.

## 1. Visão geral

Motor de **busca semântica** sobre ficheiros `.txt` internos: embeddings com **Hugging Face Transformers**, índice **FAISS** e API para devolver os **5 documentos** mais alinhados com a pergunta (configurável até 20).

## 2. Objetivos do exercício

- Gerar vetores normalizados e persistir índice FAISS.
- Servir consultas via FastAPI (`POST /buscar`).
- Extra: comparar **palavra‑chave** vs **semântica** (`GET /comparar`).

## 3. Frameworks utilizados

- **sentence-transformers / Transformers** — embeddings multilingues (por defeito MiniLM multilingue).
- **FAISS** — produto interno / similaridade.
- **Docker**.

Motivo: HF cobre bom português sem API externa; FAISS é leve e standard em RAG.

## 4. Arquitetura

```text
documentos .txt → EmbedderHF → vetores → FAISS → pergunta embedding → top‑k + scores
```

## 5. Estrutura de pastas

- `data/documentos/` — corpus de exemplo.
- `scripts/criar_indice.py` — constrói o índice em `data/indices/` (gitignored).
- `scripts/buscar.py` — CLI (`--keyword`, `--comparar`).
- `app/embeddings_hf.py`, `app/faiss_store.py`, `app/main.py`.

## 6. Como executar com Docker

```bash
cp .env.example .env  # opcional: HF_EMBEDDING_MODEL
docker compose up --build
python scripts/criar_indice.py   # dentro do contentor ou localmente com mesmo PYTHONPATH
```

Garanta que o índice existe antes de `/buscar` (senão HTTP 503).

## 7. Variáveis de ambiente

Ver `.env.example`: modelo HF opcional, caminhos, etc.

## 8. Explicação do código

- **`EmbedderHF`** — média dos tokens com máscara de atenção e normalização L2.
- **`faiss_store`** — persistência `index.faiss` + metadados dos nomes dos ficheiros.
- **`main`** — validação Pydantic e tratamento de índice em falta.

## 9. Exemplos de entrada

```json
POST /buscar
{"pergunta": "Como pedir férias?", "top_k": 5}
```

## 10. Exemplos de saída

```json
[
  {"documento": "politica_de_suporte.txt", "score": 0.91},
  {"documento": "manual_atendimento.txt", "score": 0.87}
]
```

(`score` ≈ similaridade coseno.)

## 11. Critérios de avaliação

Docker, scripts de índice e busca, exemplos reais, tratamento de erro (índice ausente).

## 12. Possíveis melhorias

Chunking por parágrafos, reranking cruzado, UI Streamlit.

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
