# Exercício 10 — CrewFinance

## 1. Visão geral

Consultoria **multiagente** (CrewAI) que produz um **relatório financeiro** a partir de um pedido em linguagem natural, com papéis de **analista**, **crítico**, **auditor** (extra) e **redator**.

## 2. Objetivos do exercício

- Definir **agentes** com responsabilidades distintas e tarefas encadeadas.
- Validar entrada com **Pydantic** (`PedidoFinanceiro`).
- Expor `POST /relatorio` via FastAPI.

## 3. Frameworks utilizados

- **CrewAI** — `Crew`, `Agent`, `Task`, processo sequencial.
- **LiteLLM** — string `gemini/...` com `GOOGLE_API_KEY`.
- **Pydantic v2**, **Docker**.

## 4. Arquitetura

```text
Pedido → Analista → Crítico → Auditor → Redator → relatório consolidado
```

## 5. Estrutura de pastas

- `app/crew_runner.py` — definição da crew e `executar_crew`.
- `app/main.py` — API.

## 6. Como executar com Docker

```bash
cp .env.example .env   # GOOGLE_API_KEY obrigatória
docker compose up --build
```

## 7. Variáveis de ambiente

`GOOGLE_API_KEY`, `GEMINI_MODEL` / variáveis CrewAI documentadas no `.env.example` da pasta.

## 8. Explicação do código

Cada tarefa injeta o output anterior via `context`; o resultado final é texto único retornado à API.

## 9. Exemplo de entrada

```json
POST /relatorio
{"pedido": "Analise o risco financeiro de uma pequena empresa com queda de receita de 20%."}
```

## 10. Exemplo de saída

```json
{"relatorio": "..." }
```

## 11. Critérios de avaliação

Crew coerente, Pydantic, Docker, README com exemplos.

## 12. Possíveis melhorias

Ferramentas com dados reais (CSV), memória partilhada, avaliação automática do relatório.

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
