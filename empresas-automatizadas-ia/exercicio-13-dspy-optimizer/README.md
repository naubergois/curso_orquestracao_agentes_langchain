# Exercício 13 — DSPy Optimizer

## 1. Visão geral

O **DSPy Optimizer** compara duas formulações de prompt (resposta curta vs. detalhada) sobre um pequeno conjunto de perguntas e calcula uma **métrica composta** (desafio extra).

## 2. Objetivos do exercício

- Declarar **assinaturas DSPy** (`RespostaCurta`, `RespostaDetalhada`).
- Executar `ChainOfThought` por pergunta e agregar scores.
- Servir resultados via API e script CLI.

## 3. Frameworks utilizados

- **DSPy** — módulos e configuração de LM (`dspy.LM` com prefixo `gemini/`).
- **FastAPI / Docker**.

## 4. Arquitetura

```text
perguntas.json → LM Gemini → duas variantes → métrica claridade/completude/precisão → médias
```

## 5. Estrutura de pastas

- `data/perguntas.json` — dataset mínimo.
- `app/dspy_pipeline.py` — avaliação.
- `scripts/run_dspy_experiment.py` — CLI.

## 6. Como executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

`POST http://localhost:8013/avaliar`

## 7. Variáveis de ambiente

`GOOGLE_API_KEY`, `GEMINI_MODEL_DSPY` (ex.: `gemini/gemini-2.0-flash`).

## 8. Explicação do código

`claridade_completude_precisao` implementa heurísticas simples; `avaliar` percorre o dataset e devolve médias globalizadas.

## 9–10. Exemplos

`POST /avaliar` sem corpo devolve JSON com `media_curta`, `media_detalhada`, `linhas[]`.

## 11. Critérios de avaliação

Dataset presente, métrica explícita, comparação antes/depois interpretável.

## 12. Possíveis melhorias

Teleprompt (Bootstrap), métrica com julgador LLM, mais exemplos de treino.

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
