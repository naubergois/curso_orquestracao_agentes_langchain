# Exercício 20 — Empresa Autônoma Integrada

## 1. Visão geral

Projeto **esqueleto** gerado para cumprir estrutura do curso (`run.sh`, Docker, pastas). Implemente o enunciado (frameworks específicos, RAG, agentes, etc.).

## 2–5. Objetivos / Frameworks / Arquitetura

Ver documentação global do curso e complete `docs/`.

## 6. Como executar *(sem ecrã — Jupyter)*

```bash
./run.sh
```

Jupyter Lab (`docker-compose.jupyter.yml`), como `exercicios/*_sem_ecra`. Notebook: `exercicio_NN_sem_ecra.ipynb` nesta pasta.

API FastAPI opcional: `./run_api.sh` (`docker-compose.yml`).

## 7. Variáveis de ambiente

Configure `GOOGLE_API_KEY` no `.env` na **raiz do repositório do curso** (o Docker Compose usa `../../.env`). Opcional: `.env` nesta pasta para sobrescrever no código.

## 8. Código e explicações detalhadas

- **`exercicio_20_sem_ecra.ipynb`** — implementação completa no Jupyter.
- **`docs/arquitetura.md`**, **`docs/explicacao_teorica.md`**, **`docs/passo_a_passo.md`**, **`docs/resultados.md`** — documentação longa por tema.
- **`app/main.py`** — API opcional (`./run_api.sh`); esqueleto até integração com o notebook.

Para regenerar notebooks/docs a partir do modelo central: `python3 scripts/generate_detalhado.py`.

## 11–12. Avaliação / melhorias

Substituir este README pelo modelo completo do curso quando o exercício estiver implementado.
