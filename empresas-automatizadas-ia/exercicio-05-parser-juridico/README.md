# Exercício 5 — Parser Jurídico

**Empresa simulada:** a **Parser Jurídico** automatiza a **leitura inicial** de demandas jurídicas informais.

## Problema de negócio

Escritórios recebem **textos longos** de clientes e precisam **estruturar** rapidamente tipo de situação, partes, prazos, risco e prioridade antes de distribuir o caso.

## Frameworks (conforme enunciado)

| Requisito | Implementação neste repo |
|-----------|---------------------------|
| **Pydantic** | `TextoDemandaIn`, `ScreeningJuridico`, `DemandaExtraida` — [`app/schemas/demanda.py`](app/schemas/demanda.py) |
| **Guardrails AI ou Instructor** | **Instructor** + provider Google (`instructor[google-genai]`), alinhado com Gemini — [`app/services/parser_juridico.py`](app/services/parser_juridico.py) |
| **FastAPI** | `POST /analisar`, `GET /health` — [`app/main.py`](app/main.py) |
| **Docker** | [`Dockerfile`](Dockerfile) + [`docker-compose.yml`](docker-compose.yml) |

> **Nota:** *Guardrails AI* poderia substituir ou reforçar a fase de screening; aqui o **gate jurídico** é um modelo Pydantic (`ScreeningJuridico`) obrigatório antes da extração.

## Conceitos

- Extração de informação guiada por schema  
- Validação automática da saída (Pydantic / retries Instructor)  
- JSON estruturado estável para integrações  
- Tratamento de erros HTTP (`422` texto não jurídico, `503` modelo/config)

## Tarefa (implementada)

API que recebe texto e extrai:

- `tipo_demanda`  
- `partes_envolvidas`  
- `prazo`  
- `risco`  
- `prioridade`  
- `resumo`  

### Arquitetura

```text
Texto jurídico
  → LLM (screening estruturado)
  → se não jurídico: HTTP 422 TEXTO_NAO_JURIDICO
  → LLM (extração estruturada)
  → Validação Pydantic / Instructor
  → JSON final (DemandaExtraida)
```

### Exemplo de saída (`200 OK`)

```json
{
  "tipo_demanda": "contratual",
  "partes_envolvidas": ["Cliente X", "Fornecedor Y"],
  "prazo": "Resposta solicitada em 15 dias.",
  "risco": "medio",
  "prioridade": "alta",
  "resumo": "Cliente relata descumprimento contratual com possível prazo de resposta curto."
}
```

## Entregáveis

| Entregável | Local |
|------------|--------|
| Endpoint `/analisar` | [`app/main.py`](app/main.py) |
| Schemas | [`app/schemas/demanda.py`](app/schemas/demanda.py) |
| Validação + screening | [`app/services/parser_juridico.py`](app/services/parser_juridico.py) |
| Documentação Markdown | Este README, [`docs/arquitetura.md`](docs/arquitetura.md), [`docs/API.md`](docs/API.md) |
| Docker | `./run_api.sh` |

### Desafio extra

**Bloqueio quando o texto não é jurídico:** primeiro passo LLM devolve `ScreeningJuridico`; se `texto_refere_questao_juridica` for `false`, a API responde **`422`** com `codigo: TEXTO_NAO_JURIDICO`.

## Como executar

### API (Docker)

```bash
./run_api.sh
```

Documentação interativa: `http://localhost:8000/docs`

Variáveis: `GOOGLE_API_KEY` no `.env` na **raiz do repositório do curso**. Opcional: `GEMINI_MODEL_EX05` ou `GEMINI_MODEL` (predef.: `gemini-2.0-flash`).

### Jupyter (opcional)

```bash
./run.sh
```

Notebook: `exercicio_05_sem_ecra.ipynb` (didático; a referência de produto é `app/`).

## Teste rápido (`curl`)

Ver exemplos em [`docs/API.md`](docs/API.md).
