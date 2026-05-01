# Curso — orquestração de agentes com LangChain

Exercícios com **Docker**, **Streamlit** (com ecrã) e **Jupyter Lab** (sem ecrã), usando **LangChain** / **LangGraph**. Os exercícios **00–03**, **05** e **06** usam a API **Google Gemini**; o **04** usa **DeepSeek** (API compatível com OpenAI) e **PostgreSQL** com dados fictícios. O **05** aprofunda **LCEL** e *prompt templates*; o **06**, **memória e histórico** na stack LangChain (só Jupyter). Resumo por pasta: [`exercicios/README.md`](exercicios/README.md).

## Início rápido

1. Clonar o repositório.
2. Copiar [`.env.example`](.env.example) para **`.env`** na raiz do repositório e preencher as chaves indicadas nos comentários (`GOOGLE_API_KEY` para a maior parte dos exercícios; `DEEPSEEK_API_KEY` para o exercício 4).
3. Ir a **`exercicios/<nome_da_pasta>/`** e executar **`./run.sh`** (Linux/macOS) ou **`run.ps1`** / **`run.cmd`** (Windows). A predefinição é subir a stack em Docker.

## Documentação no repositório

| Ficheiro | Conteúdo |
|----------|----------|
| [`exercicios/README.md`](exercicios/README.md) | Visão geral, **descrição do que faz cada exercício**, variáveis de ambiente e scripts úteis. |
| [`exemplos/`](exemplos/) | Exemplos pontuais (por exemplo mensagem de sistema em Docker). |
| [`exercicios/GUIA_NOVOS_EXERCICIOS.md`](exercicios/GUIA_NOVOS_EXERCICIOS.md) | Convenções para criar novos exercícios, compose, variáveis de ambiente e checklist. |

## Baseline

Este *baseline* consolida a estrutura `…_com_ecra` / `…_sem_ecra`, utilitários de Docker partilhados, exercício 4 com Postgres + DeepSeek e cadernos autocontidos.
