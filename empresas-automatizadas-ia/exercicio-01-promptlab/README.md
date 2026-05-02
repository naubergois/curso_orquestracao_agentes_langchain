# Exercício 01 — PromptLab Consultoria

## 1. Visão geral

A **PromptLab Consultoria** simula uma empresa que personaliza assistentes virtuais com diferentes tons e comportamentos. Este exercício automatiza a escolha do **system prompt** e devolve respostas à mesma pergunta em três perfis pedagógicos mais um perfil extra (desafio).

## 2. Objetivos do exercício

- Demonstrar `SystemMessage`, `HumanMessage` e `AIMessage` com LangChain.
- Validar entradas com **Pydantic** (enum + limites de texto).
- Expor uma **API FastAPI** testável com Docker.
- Documentar prompts de sistema de forma centralizada.
- **Desafio extra:** perfil `sarcastico_nerd` (humor nerd corporativo educado).

## 3. Frameworks utilizados

- **LangChain (`langchain-core`, `langchain-google-genai`)** — mensagens e integração com Gemini, alinhada ao resto do curso.
- **Pydantic v2** — contrato da API e validação estrita do campo `perfil`.
- **FastAPI** — endpoints REST e documentação OpenAPI em `/docs`.
- **Docker / Docker Compose** — execução reprodutível com um comando.

## 4. Arquitetura

```text
Utilizador → FastAPI → Validação Pydantic → Seleção do perfil / system prompt
    → LangChain (SystemMessage + HumanMessage) → Gemini → AIMessage → JSON
```

Detalhes em [docs/arquitetura.md](docs/arquitetura.md).

## 5. Estrutura de pastas

| Caminho | Função |
| ------- | ------ |
| `app/main.py` | Arranque Uvicorn e rotas FastAPI |
| `app/schemas/` | Modelos `PerguntaEntrada`, `RespostaSaida`, enum `PerfilAssistente` |
| `app/chains/` | Invocação do modelo com mensagens |
| `app/services/` | Textos de sistema (`prompts.py`) e fábrica do chat (`llm_factory.py`) |
| `app/agents/` | Reservado (sem agente autónomo neste exercício) |
| `app/tools/` | Reservado para evoluções |
| `app/data/` | Dados estáticos / exemplos futuros |
| `exercicio_01_sem_ecra.ipynb` | Trabalho principal *(sem ecrã)* — **código didático nas células** (sem `from app…`); `app/` espelha para a API |
| `notebooks/testes.ipynb` | Chamadas HTTP de exemplo (opcional) |
| `docs/` | Arquitetura, teoria, passos e resultados esperados |

## 6. Como executar *(sem ecrã — Jupyter, predefinição)*

Como nos exercícios `exercicios/*_sem_ecra`: **`./run.sh`** abre **Jupyter Lab** no Docker (`docker-compose.jupyter.yml`) e posiciona o Lab na pasta deste exercício. Trabalhe em [`exercicio_01_sem_ecra.ipynb`](exercicio_01_sem_ecra.ipynb).

```bash
./run.sh
# OPEN_JUPYTER_BROWSER=0 ./run.sh
# JUPYTER_PORT=8890 ./run.sh
```

**API FastAPI opcional** (mesmo código que `app/`): `./run_api.sh` ou `docker compose -f docker-compose.yml up --build` → `http://localhost:8000/docs`.

O `lib_docker_empresas.sh` faz `docker compose down` nos outros projetos desta coleção (incluindo instâncias Jupyter).

Configure o **`.env` na raiz do repositório** (ver secção 7). Referência de chaves: [.env.example](.env.example).

## 7. Variáveis de ambiente

Defina-as no **`.env` na raiz do repositório do curso** (carregado pelo Docker Compose). Referência das chaves: [.env.example](.env.example).

- **`GOOGLE_API_KEY`** (obrigatória) — também aceite `GEMINI_API_KEY` pelo cliente Google.
- **`GEMINI_MODEL`** — por omissão `gemini-2.0-flash`.
- **`GEMINI_RETRY_ATTEMPTS`**, **`GEMINI_RETRY_DELAY_SEC`** — mitigação simples para quota (429).

Opcional: `.env` na pasta deste exercício sobrepõe no modo `--local` (ver `app/main.py`).

## 8. Explicação do código

**Sem ecrã (predefinição):** [`exercicio_01_sem_ecra.ipynb`](exercicio_01_sem_ecra.ipynb) — Pydantic + quatro perfis + LangChain alinhados ao código modular abaixo.

**Documentação detalhada:** [`docs/arquitetura.md`](docs/arquitetura.md), [`docs/explicacao_teorica.md`](docs/explicacao_teorica.md), [`docs/passo_a_passo.md`](docs/passo_a_passo.md), [`docs/resultados.md`](docs/resultados.md).

**API opcional (`./run_api.sh`):**

- **`app/main.py`** — `GET /health`, `GET /perfis`, `POST /responder`, `GET /coordenacao/modos`, `POST /coordenacao`.
- **`app/schemas/pergunta.py`** — entrada/saída tipadas e enum dos perfis.
- **`app/schemas/coordenacao.py`** — modos de coordenação multi-agente + etapas observáveis.
- **`app/chains/promptlab_chain.py`** — monta `SystemMessage` + `HumanMessage`, invoca o chat com retries.
- **`app/chains/coordenacoes.py`** — cinco orquestrações entre perfis (sequencial, paralelo+síntese, debate, router, refinamento).
- **`app/services/prompts_coordenacao.py`** — prompts do sintetizador e do router.
- **`app/services/prompts.py`** — prompts documentados por perfil.
- **`app/services/llm_factory.py`** — instancia `ChatGoogleGenerativeAI`.
- **`app/agents/`**, **`app/tools/`** — estrutura do curso; sem lógica obrigatória aqui.

Regenerar notebook/docs a partir do modelo em [`scripts/generate_detalhado.py`](../scripts/generate_detalhado.py): `python3 scripts/generate_detalhado.py`.

## 9. Exemplos de entrada

```json
{
  "perfil": "professor",
  "pergunta": "O que é um agente de IA?"
}
```

Outros valores válidos para `perfil`: `tecnico`, `comercial`, `sarcastico_nerd`.

## 10. Exemplos de saída

```json
{
  "perfil": "professor",
  "resposta": "Um agente de IA é um sistema capaz de interpretar uma solicitação, decidir uma ação e usar ferramentas para executar tarefas."
}
```

(O texto exacto depende do modelo e da amostragem.)

Teste rápido:

```bash
curl -s -X POST http://localhost:8000/responder \
  -H "Content-Type: application/json" \
  -d '{"perfil":"tecnico","pergunta":"O que é RAG?"}'
```

Coordenação multi-agente (lista de modos e exemplo `router_inteligente`):

```bash
curl -s http://localhost:8000/coordenacao/modos

curl -s -X POST http://localhost:8000/coordenacao \
  -H "Content-Type: application/json" \
  -d '{"modo":"sequencial_pipeline","pergunta":"O que é um agente de IA?"}'
```

Outros valores de `modo`: `paralelo_sintese`, `debate_critico`, `router_inteligente`, `refinamento_triplo`.

## 11. Critérios de avaliação

| Critério | Como verificar |
| -------- | -------------- |
| Docker | `./run.sh` (Jupyter) ou `./run_api.sh` sobe com `.env` válido na **raiz do repo** |
| README | Este ficheiro cobre execução, env e exemplos |
| Frameworks | LangChain + Pydantic + FastAPI visíveis no código |
| Organização | Pastas `schemas`, `chains`, `services` separadas |
| Entrada/saída | JSON conforme secções 9 e 10 |
| Erros | 422 em validação; 503 com mensagem clara se o modelo falhar |
| Desafio extra | Perfil `sarcastico_nerd` listado e funcional |

## 12. Possíveis melhorias

- Cache por hash (`perfil` + `pergunta`) para demos repetidas.
- Suporte opcional a OpenAI/Azure mantendo a mesma interface Pydantic.
- Testes automáticos com `TestClient` e mocks do LLM.
- Métricas de latência por perfil.
