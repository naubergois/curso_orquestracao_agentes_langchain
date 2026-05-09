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

### Jupyter (sem ecrã)

```bash
cd exercicios/17_noticias_resumo_executivo_sem_ecra
./run.sh
```

Abrir o URL indicado (Jupyter Lab) e correr `exercicio_17_sem_ecra.ipynb`.

### Streamlit (opcional nesta pasta)

`./run_streamlit.sh` (porta **8502**): boletim + chat com o agente do ex. 18.

A interface **principal** com o mesmo pipeline e o agente 18 a incluir a *tool* `executar_boletim_noticias_ex17` está no **exercício 18** (`./run.sh`, porta **8501**) — ver `../18_agente_frontend_design/README.md`.

```bash
cd exercicios/17_noticias_resumo_executivo_sem_ecra
./run_streamlit.sh
```

Abrir **http://127.0.0.1:8502** (porta por defeito; altere com `STREAMLIT_PORT`). O *build* Docker usa a **raiz do repositório** como contexto para incluir `agente_frontend.py` do ex. 18.

Parar: `docker compose -f docker-compose.streamlit.yml down`
