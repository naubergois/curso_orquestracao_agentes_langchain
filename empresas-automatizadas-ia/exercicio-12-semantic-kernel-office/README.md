# Exercício 12 — Semantic Kernel Office

## 1. Visão geral

A **Semantic Kernel Office** automatiza tarefas administrativas: resumo, redação de e-mail, lista de tarefas e uma **skill composta** que resume uma reunião e gera e-mail de encaminhamento.

## 2. Objetivos do exercício

- Integrar **Semantic Kernel** com um serviço de chat (`OpenAIChatCompletion`) apontando para **Gemini** (OpenAI-compatível).
- Implementar **quatro skills** (`resumir`, `email`, `tarefas`, `reuniao`).
- API simples para seleção explícita da skill.

## 3. Frameworks utilizados

- **Semantic Kernel (Python)** — `ChatHistory`, `OpenAIChatCompletion`, settings de execução.
- **OpenAI SDK** — cliente assíncrono com `base_url` do Gemini.
- **Docker**.

## 4. Arquitetura

```text
Pedido HTTP → seleção da skill → ChatHistory(system,user) → Gemini → JSON/texto
```

## 5. Estrutura de pastas

- `app/office_skills.py` — lógica das skills e chamadas ao modelo.
- `app/main.py` — FastAPI `POST /executar`.

## 6. Como executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

Serviço em `http://localhost:8012`.

## 7. Variáveis de ambiente

`GOOGLE_API_KEY`, `GEMINI_MODEL_SK`, `PORT` — ver `.env.example`.

## 8. Explicação do código

`_gerar` centraliza a invocação `get_chat_message_contents`. A skill **reuniao** pede JSON estruturado (resumo + e-mail).

## 9. Exemplos de entrada

```json
POST /executar
{"skill": "resumir", "texto": "Texto longo ..."}
```

## 10. Exemplos de saída

```json
{"skill": "resumir", "resultado": "..."}
```

Skill `reuniao`: `resultado` é objeto JSON com `resumo`, `assunto_email`, `corpo_email` quando o modelo obedece ao formato.

## 11. Critérios de avaliação

Uso real do conector SK, clareza das skills, Docker e README.

## 12. Possíveis melhorias

Plugins SK em pastas (`skprompt.txt`), planner automático, testes de regressão por skill.

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
