# Exercício 15 — três agentes de vendas (sem ecrã, Docker)

Demonstração com **PostgreSQL** e três agentes LangChain (**DeepSeek** via `ChatOpenAI`):

| Agente | Papel |
|--------|--------|
| Estoque | Consulta produtos, ajusta stock, regista vendas |
| Marketing | Lê produtos com stock, propõe copy e grava campanhas em `campanhas_marketing` |
| Análise | Agrega vendas e extrai insights |

## Pré-requisitos

- Docker + plugin `docker compose`
- `.env` na raiz do repositório com **`DEEPSEEK_API_KEY`** (opcional: `DEEPSEEK_MODEL`, `DEEPSEEK_API_BASE`)

## Arranque

```bash
cd exercicios/15_vendas_tres_agentes_sem_ecra
./run.sh
```

Abre o Jupyter Lab e o notebook `exercicio_15_sem_ecra.ipynb`.

- **Postgres no host:** `localhost:5435` (predefinição), base `vendas_demo`, utilizador `curso`, palavra-passe `curso`.
- **Jupyter:** `http://127.0.0.1:8888`

## Parar

```bash
cd exercicios/15_vendas_tres_agentes_sem_ecra
docker compose -f docker-compose.jupyter.yml down
```

## Nota pedagógica

Os dados são **fictícios**. Os agentes são independentes (não há orquestração automática entre eles); no notebook podes experimentar mensagens e combinar fluxos manualmente.
