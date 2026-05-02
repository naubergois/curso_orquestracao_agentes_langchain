# Exercício 14 — TutorGraph

## 1. Visão geral

**TutorGraph** é um tutor adaptativo com fluxo em grafo: diagnostica, explica, propõe exercício, corrige e revisa; se o aluno falhar, **volta a explicar** (desafio extra).

## 2. Objetivos do exercício

- Modelar o fluxo em **LangGraph** com estado explícito.
- Tipar pedidos/respostas HTTP com **Pydantic**.
- Registar **logs** por nó.

## 3. Frameworks utilizados

- **LangGraph** — `StateGraph`, ramificação condicional.
- **LangChain Google GenAI** — Gemini.
- **Pydantic v2**.

## 4. Arquitetura

```text
diagnosticar → explicar → exercitar → corrigir ─┬→ revisar → fim
                                                 └→ explicar (retry)
```

## 5. Estrutura de pastas

- `app/tutor_graph.py` — nós e compilação do grafo.
- `app/schemas.py` — `TutorPedido`, `TutorResultado`.
- `app/main.py` — `POST /sessao`.

## 6. Como executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

`http://localhost:8014`

## 7. Variáveis de ambiente

`GOOGLE_API_KEY`, `GEMINI_MODEL`.

## 8. Explicação do código

Cada nó chama Gemini com instruções JSON onde necessário; `Annotated[list,str], operator.add` acumula logs.

## 9. Exemplo de entrada

```json
{"tema": "Probabilidade condicional", "resposta_aluno": "...", "nivel": "iniciante"}
```

## 10. Exemplo de saída

Campos `explicacao`, `exercicio`, `correto`, `feedback`, `logs`.

## 11. Critérios de avaliação

Grafo completo, ramificação correta, Pydantic na API.

## 12. Possíveis melhorias

Memória de sessão multi-turno, banco de exercícios, avaliação automática mais robusta.

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
