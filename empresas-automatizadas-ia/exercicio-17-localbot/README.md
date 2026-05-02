# Exercício 17 — LocalBot

## 1. Visão geral

**LocalBot** expõe um chatbot que usa **Ollama** via LangChain, com opção de **comparar** com modelo na nuvem (Gemini), destacando privacidade vs. qualidade.

## 2. Objetivos do exercício

- Integrar **ChatOllama** (`langchain-community`).
- Suportar Ollama **no host** ou **em container** (variável `OLLAMA_BASE_URL`).
- **Docker Compose** com serviço `ollama` opcional.

## 3. Frameworks utilizados

- **Ollama**, **LangChain**, **FastAPI**, **Docker**.

## 4. Arquitetura

```text
Cliente → FastAPI → ChatOllama (Ollama) → resposta
           └→ (opcional) Gemini para comparação
```

## 5. Estrutura de pastas

- `app/chat_local.py` — fabrica LLMs locais/remotos.
- `app/main.py` — `/chat` e `/chat/compare`.

## 6. Como executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

API `http://localhost:8017`. No primeiro arranque do Ollama em container:

```bash
docker exec -it ollama_localbot ollama pull llama3.2
```

## 7. Variáveis de ambiente

`OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `GOOGLE_API_KEY` (só para `/chat/compare`).

## 8. Explicação do código

`/chat` usa apenas Ollama; comparação chama sequencialmente local + nuvem.

## 9–10. Exemplos

`POST /chat {"mensagem":"Olá"}` — `POST /chat/compare` precisa de `GOOGLE_API_KEY`.

## 11. Critérios de avaliação

README explica host vs. container, compose funcional.

## 12. Possíveis melhorias

Cache de conversação, function calling local, métricas de latência.

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
