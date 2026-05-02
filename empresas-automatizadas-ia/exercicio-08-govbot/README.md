# Exercício 08 — GovBot Cidadão

## 1. Visão geral

Chatbot de **atendimento público fictício** que responde com base em documentos Markdown, usando **Haystack 2.x**, **Qdrant** como vector store e **Gemini** para geração.

## 2. Objetivos do exercício

- Pipeline consulta: embedding → retriever Qdrant → LLM com contexto.
- Resposta com **fontes** citadas.
- Extra: **classificar demanda** (imposto, protocolo, serviço urbano, licença, geral).

## 3. Frameworks utilizados

- **Haystack** — componentes de retrieval e geradores Google GenAI.
- **Qdrant** — persistência vetorial no Docker Compose.
- **Sentence Transformers** — embeddings 384 dim (alinhado ao retriever).
- **Docker Compose**.

## 4. Arquitetura

```text
Pergunta → embedder → Qdrant retriever → Gemini (com trechos) → resposta + fontes + classe
```

## 5. Estrutura de pastas

- `data/publicos/*.md` — documentos fictícios.
- `app/govbot_service.py` — indexação e pipeline.
- `docker-compose.yml` — `app` + `qdrant`.

## 6. Como executar com Docker

```bash
cp .env.example .env   # GOOGLE_API_KEY, QDRANT_URL=http://qdrant:6333
docker compose up --build
```

## 7. Variáveis de ambiente

`GOOGLE_API_KEY`, `QDRANT_URL`, modelo Gemini opcional — ver `.env.example`.

## 8. Explicação do código

Serviço garante coleção Qdrant criada, escrita de documentos na primeira subida e reuso em chamadas seguintes.

## 9. Exemplo de entrada

```json
POST /chat
{"mensagem": "Como consultar débitos de IPTU?"}
```

## 10. Exemplo de saída

Campos `classificacao_demanda`, `resposta`, `fontes[]` com documento e excerto.

## 11. Critérios de avaliação

Haystack + Qdrant corretamente ligados, Docker, README e exemplos.

## 12. Possíveis melhorias

Cache de queries, autenticação, avaliação offline do retrieval.

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
