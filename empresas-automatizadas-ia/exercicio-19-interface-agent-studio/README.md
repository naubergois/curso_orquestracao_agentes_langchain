# Exercício 19 — Interface Agent Studio

## 1. Visão geral

Duas UIs (**Streamlit** e **Gradio**) sobre o **mesmo agente** Python, para comparar velocidade de prototipagem e UX.

## 2. Objetivos do exercício

- Parametrizar **modelo**, **tom** e **temperatura** (extra).
- Mostrar trade-offs entre frameworks de UI.

## 3. Frameworks utilizados

- **Streamlit**, **Gradio**, **LangChain Google GenAI**, **Docker Compose**.

## 4. Arquitetura

```text
Streamlit/Gradio → app/agent_shared.responder → Gemini
```

## 5. Estrutura de pastas

- `streamlit_app.py`, `gradio_app.py`, `app/agent_shared.py`.

## 6. Como executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

- Streamlit: `http://localhost:8519`
- Gradio: `http://localhost:7869`

## 7. Variáveis de ambiente

`GOOGLE_API_KEY` na raiz do curso (`../../.env`) ou nesta pasta.

## 8. Comparação rápida

| Aspeto | Streamlit | Gradio |
| --- | --- | --- |
| Layout | excelente para dashboards | rápido para demos ML |
| Estado | reruns completos | handlers por evento |
| Deploy | container simples | idem |

## 9–10. Exemplos

Interfaces gráficas — introduzir mensagem e observar resposta com diferentes temperaturas.

## 11. Critérios de avaliação

Duas apps funcionais, README comparativo, Docker.

## 12. Possíveis melhorias

Upload de ficheiros, histórico de chat, temas custom.

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
