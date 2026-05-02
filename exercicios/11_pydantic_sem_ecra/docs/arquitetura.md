# Arquitetura — Exercício 11 (Pydantic)

## Fluxo conceptual

```text
Dados brutos (dict, JSON, texto LLM)
  → model_validate / model_validate_json
  → BaseModel (campos tipados + validadores)
  → model_dump / JSON Schema
  → APIs, pipelines LangChain, armazenamento
```

## Neste exercício

- **Núcleo:** Pydantic v2 **sem rede** — validação local.
- **Extensão opcional:** `ChatGoogleGenerativeAI.with_structured_output(Modelo)` — o modelo devolve dados compatíveis com o schema.

## Docker

Um serviço **Jupyter** (`docker-compose.jupyter.yml`) com dependências em `requirements.txt`.
