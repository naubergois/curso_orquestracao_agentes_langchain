# Teoria — Pydantic v2 (resumo)

## Por que Pydantic?

Garante **tipos**, **defaults** e **regras de negócio** antes de usar dados em chains, bases de dados ou UI. Erros falham **cedo** com mensagens claras.

## `BaseModel` e `Field`

- Campos têm **tipo** (`str`, `int`, `list[...]`, modelos aninhados).
- `Field(default=...)`, `description=` (útil para JSON Schema / LLMs), `ge`, `le`, `min_length`, etc.

## `field_validator`

Funções que transformam ou rejeitam **um campo** (normalizar email, capitalizar, limitar enum).

## `model_validator`

Validação **entre campos** (`mode='after'` quando já existem valores instanciados).

## Serialização

- `model_dump()` → `dict` Python (adequado a JSON).
- `model_dump_json()` → `str` JSON.
- `model_validate_json(str)` → instância.

## JSON Schema

`Model.model_json_schema()` expõe o schema — base para ferramentas e *structured output*.
