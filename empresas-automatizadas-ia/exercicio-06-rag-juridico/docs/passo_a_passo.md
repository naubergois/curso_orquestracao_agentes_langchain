# Passo a passo — Exercício 06: RAG Jurídico

## 1. Ambiente
1. Na **raiz do repositório**, configure `.env` com `GOOGLE_API_KEY` (e variáveis opcionais do enunciado).
2. Na pasta `exercicio-06-rag-juridico`, execute `./run.sh` para Jupyter Lab.

## 2. Notebook
Abra e execute na ordem **`exercicio_06_sem_ecra.ipynb`** (kernel Python 3).

## 3. Artefactos gerados
Alguns notebooks escrevem ficheiros (`historico_export.json`, índices em `./tmp_vector`, etc.). Não commite dados sensíveis.

## 4. Modos opcionais
- **API / Streamlit:** ver `run_api.sh` ou `run_streamlit.sh` conforme pasta.

## 5. Parar containers
```bash
docker compose -f docker-compose.jupyter.yml down
```
