# Exercício 6 — RAG Jurídico

**Empresa simulada:** a **RAG Jurídico** oferece consulta automatizada a **documentos internos** fictícios de um escritório (contratos, pareceres, normas).

## Problema de negócio

Advogados precisam **encontrar respostas** rápidas em contratos, pareceres e normas internas sem reler tudo manualmente.

## Frameworks obrigatórios

| Framework | Uso |
|-----------|-----|
| **LlamaIndex** | Loaders, índice vetorial, query engine com síntese |
| **ChromaDB** | Persistência do vector store (`data/chroma_juridico/`) |
| **Docker** | [`Dockerfile`](Dockerfile) + [`docker-compose.yml`](docker-compose.yml) |

Embeddings e LLM via **Google Gemini** (SDK compatível com LlamaIndex: `llama-index-embeddings-google-genai`, `llama-index-llms-google-genai`). Variável **`GOOGLE_API_KEY`** na raiz do repositório do curso.

## Conceitos

Carregamento de documentos → segmentação (*chunks*) → **embeddings** → **ChromaDB** → **retriever** → resposta com contexto.

## Arquitetura

```text
Documentos (data/juridico/*.md)
  → Loader (SimpleDirectoryReader)
  → Chunks + embeddings (LlamaIndex + Gemini embeddings)
  → ChromaDB (persistente)
  → Retriever + LLM (Gemini)
  → Resposta + trechos recuperados
```

## Entregáveis

| Entregável | Local |
|------------|--------|
| Base de documentos | [`data/juridico/`](data/juridico/) |
| Script de indexação | [`scripts/indexar.py`](scripts/indexar.py) |
| Script de consulta | [`scripts/consultar.py`](scripts/consultar.py) |
| Resposta com trechos | Campo `fontes[]` (API e CLI) |
| Docker | `./run_api.sh` |
| Documentação Markdown | Este ficheiro, [`docs/arquitetura.md`](docs/arquitetura.md), [`docs/API.md`](docs/API.md) |

### Desafio extra

A API **`POST /perguntar`** e o script **`consultar.py`** devolvem também os **documentos/trechos mais relevantes** (`fontes`: `arquivo`, `score`, `trecho`).

### Exemplo de pergunta

> Qual é o prazo para resposta contratual segundo o documento?

(Resposta esperada alinhada com **15 dias úteis** nas normas/contrato fictícios — sujeita à síntese do modelo.)

## Fluxo rápido

1. **Variáveis:** `GOOGLE_API_KEY` no `.env` na raiz do repo do curso.
2. **Subir API:** `./run_api.sh` (ou `./run_api.sh --fg`).
3. **Indexar** (uma vez, ou após mudar documentos):

```bash
docker compose exec app python scripts/indexar.py
```

(No host, com o mesmo código montado: `python scripts/indexar.py`.)

4. **Consultar:**

```bash
docker compose exec app python scripts/consultar.py "Qual é o prazo para resposta contratual segundo o documento?"
```

Ou **`POST /perguntar`** — ver [`docs/API.md`](docs/API.md).

## Jupyter (opcional)

```bash
./run.sh
```

Notebook `exercicio_06_sem_ecra.ipynb` pode ser usado para explorar o tema; a implementação de referência productiva está em **`app/rag/`** e **`scripts/`**.

**Build (Chroma em Apple Silicon / aarch64):** `Dockerfile.jupyter` usa `minimal-notebook:python-3.12.11` (não `latest`) para evitar Python 3.13 sem wheel do `chroma-hnswlib` e falhas de compilação («Unsupported compiler»).

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
