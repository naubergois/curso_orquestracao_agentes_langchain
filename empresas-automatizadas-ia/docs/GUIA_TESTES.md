# Guia de testes — Empresas automatizadas com IA

Este documento descreve como executar e interpretar os **testes automatizados** do monorepo `empresas-automatizadas-ia/`, garantindo que cada pasta `exercicio-NN-*` continua importável e que as APIs FastAPI respondem em `/health`.

## 1. Requisitos

- Python **3.11+** (alinhado aos `Dockerfile`; **3.12** também é usado nos notebooks Jupyter).
- Ferramentas: `pip`, `pytest`, `httpx` (via `requirements-dev.txt`).

## 2. Instalação de dependências

Cada empresa tem o seu `requirements.txt`. Para validar **todas** as empresas na mesma máquina (ambiente tipo “dev full stack”):

```bash
cd empresas-automatizadas-ia
pip install -r requirements-dev.txt
./scripts/install_test_deps.sh
```

O script percorre `exercicio-*/requirements.txt` por ordem. Podem surgir **avisos de conflito** do resolver do `pip` quando duas empresas pedem versões diferentes do mesmo pacote; nesse caso preferível:

- usar **um virtualenv por empresa**, ou  
- validar cada empresa dentro do **respectivo contentor Docker** (`docker compose run … pytest`).

## 3. Executar os testes

Na raiz `empresas-automatizadas-ia/`:

```bash
# Smoke tests (sem chamadas pagas à API Gemini)
pytest tests -m "not integration"

# Opcional: integração real (requer GOOGLE_API_KEY)
pytest tests -m integration
```

Ficheiros principais:

| Ficheiro | Função |
|----------|--------|
| `tests/conftest.py` | Lista `FASTAPI_EXERCISES`, helper `app_test_client()`, `pytest.skip` se faltar dependência. |
| `tests/test_fastapi_health.py` | `GET /health` → `200` e `{"status":"ok"}` para cada API FastAPI. |
| `tests/test_ex02_streamlit_helpers.py` | Funções puras do exercício 02 (Streamlit). |
| `tests/test_ex07_busca_semantica.py` | `POST /buscar` sem índice → `503` ou `500` (comportamento esperado sem `criar_indice`). |
| `tests/test_ex13_dspy_metric.py` | Métrica DSPy sem LLM (`importorskip("dspy")`). |
| `tests/test_ex19_agent_shared_import.py` | Import do agente partilhado Gradio/Streamlit. |
| `tests/test_integration_optional.py` | `POST /resumir` no ex. 18 com Gemini real (`pytest.mark.integration`). |

## 4. Empresas sem FastAPI em `app/main.py`

- **Exercício 02 — Atendimento 360:** `app/main.py` é a app **Streamlit**; os testes cobrem helpers (`_historico_para_mensagens`).
- **Exercício 19 — Interface Agent Studio:** não há instância FastAPI `app`; testa-se `app/agent_shared.py`.

## 5. Compatibilidade LangGraph / LangChain

Os exercícios **09, 14, 15 e 20** fixam `langgraph>=0.2,<0.3` para permanecerem compatíveis com **`langchain-core` 0.3.x**. Instalar `langgraph 1.x` ao lado de `langchain-core 0.3` quebra o import de `create_react_agent`.

## 6. Conflitos conhecidos de pacotes

- **ChromaDB:** `exercicio-20` usa `chromadb<0.7`; outras libs (ex.: versões novas de `crewai`) podem pedir Chroma 1.x — evite misturar no mesmo venv ou use Docker por exercício.
- **Google GenAI:** migração gradual de `google.generativeai` para `google.genai` (avisos do Instructor/Gemini).

## 7. Integração contínua (sugestão)

1. Job com `pip install -r requirements-dev.txt` + `./scripts/install_test_deps.sh` numa imagem **Python 3.11-slim**.  
2. `pytest tests -m "not integration"`.  
3. Job opcional com segredo `GOOGLE_API_KEY`: `pytest tests -m integration`.

## 8. Índices e serviços externos

| Empresa | Nota |
|---------|------|
| **07** | Construir índice FAISS antes de esperar `200` em `/buscar`. |
| **06, 08, 20** | Chroma/Qdrant populados na primeira execução da app ou via scripts. |
| **17** | Ollama deve estar a correr e o modelo puxado (`ollama pull …`). |

Estes pontos não bloqueiam o smoke test `/health`, mas bloqueiam testes de integração específicos se não estiverem preparados.

## 9. Cobertura por exercício (resumo)

| Ex. | Pasta | O que o pytest cobre |
|-----|--------|----------------------|
| 01–06, 08–18, 20 | `exercicio-0N-*` com FastAPI | `GET /health` |
| 07 | busca-semantica | idem + `POST /buscar` aceita `503` sem índice |
| 02 | atendimento-360 | `_historico_para_mensagens` (Streamlit) |
| 13 | dspy-optimizer | métrica `claridade_completude_precisao` se `dspy` instalado |
| 19 | interface-agent-studio | import de `app.agent_shared.responder` |
| 18 | *(marcador `integration`)* | `POST /resumir` com Gemini real |

## 10. Reparo aplicado (pacotes `app`)

Os exercícios **14** e **18** não devem ter pastas vazias `app/schemas/` ou `app/chains/` com `__init__.py` — isso **sobrepõe** os ficheiros `schemas.py` e `chains.py` e quebra os imports. Mantém apenas os ficheiros `.py` ao mesmo nível de `main.py`.
