# Exercícios (LangChain)

Pastas numeradas com exercícios **com ecrã** (`…_com_ecra`, Streamlit + Docker) e **sem ecrã** (`…_sem_ecra`, Jupyter Lab + Docker), mais utilitários partilhados.

- **Gemini (Google AI):** exercícios **00–03** — variável **`GOOGLE_API_KEY`** e, consoante o exercício, **`GEMINI_MODEL`** (ver `.env.example`).
- **DeepSeek:** exercício **04** — **`DEEPSEEK_API_KEY`**, `DEEPSEEK_MODEL` (predef.: `deepseek-chat`), `DEEPSEEK_API_BASE`; o compose define `DATABASE_URL` para o PostgreSQL no contentor.

## Início rápido

1. Copiar `.env.example` para **`.env` na raiz do repositório** e definir as chaves necessárias ao exercício que fores correr.
2. Entrar na pasta do exercício e seguir o `run.sh` / `run.ps1` / `run.cmd` (predefinição: **Docker**).

## Documentação completa

**[GUIA_NOVOS_EXERCICIOS.md](./GUIA_NOVOS_EXERCICIOS.md)** — como criar Docker para novos exercícios, convenções de pastas, variáveis de ambiente, checklists e padrões de qualidade (para humanos e para agentes de IA).

## Scripts úteis (nesta pasta)

| Script | Descrição |
|--------|-----------|
| `rebuild_all_docker.sh` / `.ps1` | Reconstrói as imagens de **todos** os composes dos exercícios (`build --pull`). |
| `update_notebooks.sh` / `.ps1` | Limpa **outputs** dos `.ipynb` em `exercicios/` (útil antes de commit). |
| `lib_docker_exercicios.sh` / `.ps1` | Usado pelos `run_*` — para stacks paralelos não ficarem a competir pela mesma porta. |
| `gerar_codigo_completo_txt.py` | Gera `CODIGO_COMPLETO.txt` a partir dos cadernos `…_sem_ecra`. |

## Estrutura típica

- `00_alo_mundo` — Jupyter (predefinido) ou `main.py` uma vez (`./run.sh --once`).
- `01_…_com_ecra` / `01_…_sem_ecra` — chat com histórico.
- `02_…_com_ecra` / `02_…_sem_ecra` — persona com `SystemMessage`.
- `03_calculadora` — agente com ferramenta e LangGraph (Streamlit).
- `03_calculadora_sem_ecra` — mesmo exercício em Jupyter (`./run.sh`).
- `04_fatores_risco_pacientes` — agente + PostgreSQL (dados fictícios); **DeepSeek** no Streamlit (barra de progresso, um paciente de cada vez).
- `04_fatores_risco_pacientes_sem_ecra` — mesmo tema em Jupyter + Postgres + **DeepSeek** (`run_jupyter.sh`). A pasta `init_db/` inicializa o schema no Docker; a **primeira célula** do caderno pode aplicar o mesmo schema se a base tiver sido criada vazia (volume antigo).

## Exemplo isolado

Em `../exemplos/01_system_message_docker/` há um exemplo mínimo de mensagem de sistema com Docker (ver `README` ou comentários nessa pasta, se existirem).
