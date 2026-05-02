# Exercício 11 — AutoGen Research Lab

## 1. Visão geral

A **AutoGen Research Lab** simula relatórios de pesquisa gerados por debate entre agentes (pesquisador, crítico e sintetizador), reduzindo respostas “bonitas mas fracas” ao expor críticas antes da síntese final.

## 2. Objetivos do exercício

- Orquestrar **três agentes AutoGen** num grupo sequencial (round-robin).
- Registrar **logs** da conversa em `data/logs/debate.jsonl`.
- Expor **API** para tema + número de voltas (desafio extra).
- Containerizar com **Docker Compose**.

## 3. Frameworks utilizados

- **AutoGen AgentChat** — equipas e terminação por número máximo de mensagens.
- **autogen-ext OpenAI** — cliente compatível com o endpoint OpenAI do **Gemini**.
- **Docker** — reprodutibilidade.

## 4. Arquitetura

```text
Tema → RoundRobinGroupChat [pesquisador, critico, sintetizador]
    → mensagens → log JSONL + relatório final (última mensagem)
```

## 5. Estrutura de pastas

- `app/main.py` — FastAPI (`POST /debate`).
- `app/autogen_flow.py` — criação dos agentes e execução assíncrona.
- `scripts/run_autogen_lab.py` — execução em CLI.
- `data/logs/` — conversas persistidas.

## 6. Como executar com Docker

```bash
cp .env.example .env   # preencher GOOGLE_API_KEY
docker compose up --build
```

API em `http://localhost:8011` (mapeamento `8011:8000`).

## 7. Variáveis de ambiente

Ver `.env.example`: `GOOGLE_API_KEY`, `GEMINI_MODEL_EX11`, `PORT`.

## 8. Explicação do código

- **`autogen_flow.executar_debate`** — instancia `OpenAIChatCompletionClient` com `base_url` do Gemini, monta `RoundRobinGroupChat` e limita mensagens com `MaxMessageTermination`.
- **`main.py`** — valida entrada Pydantic e devolve log + relatório final.

## 9. Exemplos de entrada

```json
POST /debate
{"tema": "Impactos da IA generativa em suporte técnico.", "rodadas": 4}
```

## 10. Exemplos de saída

Campo `mensagens`: lista `{ "role": "...", "content": "..." }`; `relatorio_final`: texto da última mensagem.

## 11. Critérios de avaliação

Funcionalidade Docker, uso correto do AutoGen, logs, documentação e tratamento de erros (chave em falta).

## 12. Possíveis melhorias

Condição de paragem por menção (`TERMINATE`), mais agentes, persistência vectorial para fontes.

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
