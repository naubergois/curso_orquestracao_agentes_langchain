# Exercício 17 — notícias do dia, Pydantic e resumo executivo (sem ecrã)

Demonstra:

- **Tool** `pesquisa_noticias_web` (DuckDuckGo) para recolher trechos da Web;
- **Agente de pesquisa** (`create_agent` + Gemini) com várias consultas;
- **Saída estruturada** Pydantic (`BoletimNoticias`, `NoticiaItem`, `ResumoExecutivo`);
- **Indicadores** agregados (Python + tabela `pandas` no caderno);
- **Agente redactor** (Markdown executivo, sem *tools*).

## Pré-requisitos

- `GOOGLE_API_KEY` no `.env` na raiz do repositório;
- **Rede** no contentor (pesquisa Web).

Opcional: `GEMINI_MODEL_EX17` (senão usa `GEMINI_MODEL`). Consulta por defeito alterável com `EX17_CONSULTA` no ambiente.

## Executar

```bash
cd exercicios/17_noticias_resumo_executivo_sem_ecra
./run.sh
```

Abrir o URL indicado (Jupyter Lab) e correr `exercicio_17_sem_ecra.ipynb`.
