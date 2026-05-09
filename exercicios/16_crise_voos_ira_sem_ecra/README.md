# Exercício 16 — crise de voos internacionais simulada (sem ecrã, Docker)

Cenário **100 % fictício** para o curso: companhia **DemoAir**, rotas internacionais e uma **crise operacional simulada** com voos **cancelados** ligados ao aeroporto **IKA** (exposição à região do Irão nos dados de demonstração).

Três agentes LangChain (**DeepSeek**) com ferramentas sobre **PostgreSQL**:

| Agente | Função |
|--------|--------|
| **Marketing / comunicação** | Lê cancelamentos e passageiros afetados; regista **campanhas** em `campanhas_comunicacao` |
| **Remarcação** | Lista reservas em voos cancelados, propõe **alternativas** (mesmo destino), executa `remarcar_reserva` |
| **Risco e crise** | Resumo operacional, exposição IKA, **regista avaliações** em `avaliacoes_risco` |

## Pré-requisitos

- Docker + `docker compose`
- `.env` na raiz com **`DEEPSEEK_API_KEY`** (opcional: `DEEPSEEK_MODEL`, `DEEPSEEK_API_BASE`)

## Arranque

```bash
cd exercicios/16_crise_voos_ira_sem_ecra
./run.sh
```

- **Jupyter:** http://127.0.0.1:8888 — notebook `exercicio_16_sem_ecra.ipynb`
- **Postgres (host):** `localhost:5436`, base `crise_voos_demo`, utilizador `curso`, palavra-passe `curso`

## Parar

```bash
docker compose -f docker-compose.jupyter.yml down
```

## Aviso

Não utilizar estes dados ou mensagens como fonte de informação real sobre conflitos ou segurança aérea. É material **pedagógico** de orquestração de agentes.
