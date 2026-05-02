# Arquitetura — Exercício 03: EduPrompt Academy

## Visão técnica

Quatro **templates** (`ChatPromptTemplate`) e quatro **pipelines LCEL** independentes:

- `chain_explicacao`, `chain_exercicios`, `chain_resumo` — núcleo pedagógico.
- `chain_narrativa_nerd` — extra humorístico.

Todas seguem: **prompt → `ChatGoogleGenerativeAI` → `StrOutputParser`**.

## Fluxo (uma chain)

```text
{tema, nivel} → ChatPromptTemplate → Gemini → StrOutputParser → str
```

## Paralelismo LCEL

`RunnableParallel` combina as três chains principais num único `invoke`, expondo chaves `explicacao`, `exercicios`, `resumo`. A função `gerar_pacote_educacional` acrescenta o campo `markdown` com cabeçalhos `##`.

## Componentes

| Ficheiro | Papel |
|----------|--------|
| [`app/chains/eduprompt_chains.py`](../app/chains/eduprompt_chains.py) | Templates + factories + paralelo + Markdown |
| [`app/main.py`](../app/main.py) | FastAPI opcional (`/eduprompt/pacote`, `/eduprompt/narrativa-nerd`) |
| [`exercicio_03_sem_ecra.ipynb`](../exercicio_03_sem_ecra.ipynb) | **Implementação principal** sem ecrã — código e teoria inline (sem depender de `import app.chains`) |

## Docker

- **API:** `docker compose up --build` — porta 8000.
- **Jupyter:** `docker compose -f docker-compose.jupyter.yml up --build` — via `./run.sh`.
