# Exercício 09 — HelpDesk Agent

## 1. Visão geral

Agente de suporte com **quatro ferramentas**: abrir chamado, consultar estado, classificar problema e **estimar prioridade** (extra), exposto via **FastAPI** `/chat` com registo de chamadas em JSONL.

## 2. Objetivos do exercício

- Agente **LangGraph** `create_react_agent` com decisão sobre tools.
- Persistir **logs** das invocações das ferramentas.
- Container Docker.

## 3. Frameworks utilizados

- **LangGraph / LangChain** — agente ReAct + tools tipadas.
- **FastAPI**.
- **Gemini** via LangChain Google GenAI.

## 4. Arquitetura

```text
Mensagem → agente → escolha da tool → execução → mensagem final ao utilizador
```

## 5. Estrutura de pastas

- `app/agent_core.py` — definição das tools e grafo.
- `app/main.py` — endpoint `/chat`.
- `data/logs/agent_calls.jsonl` — trilho de auditoria simples.

## 6. Como executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

## 7. Variáveis de ambiente

`GOOGLE_API_KEY`, modelo opcional, `PORT`.

## 8. Explicação do código

As tools devolvem texto estruturado para o modelo sintetizar a resposta final; cada chamada é registada com timestamp e argumentos.

## 9–10. Exemplos

`POST /chat {"mensagem":"O PC não liga à rede Wi‑Fi da empresa.","thread_id":"opcional"}` → classificação + sugestão de abertura de chamado.

## 11. Critérios de avaliação

Três tools obrigatórias + uma extra, logs, tratamento de erro LLM.

## 12. Possíveis melhorias

Integração com sistema real de tickets, memória persistente por utilizador, políticas RBAC.

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
