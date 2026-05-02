# Exercício 20 — Empresa Autónoma Integrada

## 1. Visão geral

Projeto integrador que combina **classificação da demanda**, **RAG com Chroma**, **agente especialista**, **revisor**, **relatório interno**, **avaliação automática** (extra), **API FastAPI**, **UI Streamlit** e **LangSmith** opcional.

## 2. Objetivos do exercício

- Simular uma micro “empresa autónoma” com pipeline único acionável por HTTP.
- Persistir embeddings em volume Docker (`chroma_data`).

## 3. Frameworks utilizados

- **LangGraph**, **LangChain**, **ChromaDB**, **Gemini (chat + embeddings)**, **Streamlit**, **LangSmith**, **Docker Compose**.

## 4. Arquitetura

```text
Mensagem → classificar → RAG → especialista → revisor → relatório → avaliação
```

## 5. Estrutura de pastas

- `data/documentos/` — Markdown fictícios.
- `app/rag_store.py` — índice único com flag `.indexed_ok`.
- `app/empresa_graph.py` — LangGraph sequencial.
- `streamlit_app.py` — consome `API_URL`.

## 6. Como executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

- API: `http://localhost:8020`
- UI: `http://localhost:8520`

## 7. Variáveis de ambiente

`GOOGLE_API_KEY`, `GEMINI_MODEL`, `GEMINI_EMBED_MODEL`, LangSmith.

## 8. Explicação do código

`formatar_contexto` usa `similarity_search_with_score`; o grafo devolve também `avaliacao_automatica` em JSON textual.

## 9–10. Exemplos

`POST /pipeline {"mensagem":"Quero reembolso em 45 dias, é possível?"}` — deve citar políticas internas.

## 11. Critérios de avaliação

Compose completo, RAG real, observabilidade documentada.

## 12. Possíveis melhorias

Haystack+Qdrant em paralelo, CrewAI para papéis humanos, autenticação na API.

Após alterar ficheiros em `data/documentos/`, apague `chroma_data/.indexed_ok` (e opcionalmente o diretório `chroma_data/`) para forçar nova indexação.

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
