# Empresas automatizadas com IA

Conjunto de **20 exercícios** em cenários de **negócio** (marketing, jurídico, helpdesk, crews, LangGraph, etc.). Funciona em **paralelo** aos exercícios da pasta [`exercicios/`](../exercicios/README.md) do mesmo repositório: mesma ideia de **Docker + Jupyter** por defeito e **mesmo ficheiro `.env` na raiz** do repo.

O modo **predefinido** segue o padrão **`exercicios/*_sem_ecra`**: **Jupyter Lab no Docker**, sem Streamlit/FastAPI obrigatório — trabalho principal no notebook `exercicio_NN_sem_ecra.ipynb`.

## Fluxo principal *(sem ecrã)*

```bash
cd empresas-automatizadas-ia/exercicio-NN-nome
./run.sh
```

- Abre Jupyter em `http://127.0.0.1:8888` (sem token; só localhost).
- `OPEN_JUPYTER_BROWSER=0 ./run.sh` — não abre o browser.
- `JUPYTER_PORT=8890 ./run.sh` — outra porta.

`./run.sh` chama `run_jupyter.sh`, que usa `docker-compose.jupyter.yml` e monta a **raiz do repositório** em `/home/jovyan/work/repo`, com `working_dir` na pasta do exercício (como nos `sem_ecra` do curso).

## Índice das pastas

| # | Pasta |
|---|--------|
| 01 | [`exercicio-01-promptlab`](exercicio-01-promptlab/) |
| 02 | [`exercicio-02-atendimento-360`](exercicio-02-atendimento-360/) |
| 03 | [`exercicio-03-eduprompt`](exercicio-03-eduprompt/) |
| 04 | [`exercicio-04-fewshot-marketing`](exercicio-04-fewshot-marketing/) |
| 05 | [`exercicio-05-parser-juridico`](exercicio-05-parser-juridico/) |
| 06 | [`exercicio-06-rag-juridico`](exercicio-06-rag-juridico/) |
| 07 | [`exercicio-07-busca-semantica`](exercicio-07-busca-semantica/) |
| 08 | [`exercicio-08-govbot`](exercicio-08-govbot/) |
| 09 | [`exercicio-09-helpdesk-agent`](exercicio-09-helpdesk-agent/) |
| 10 | [`exercicio-10-crewfinance`](exercicio-10-crewfinance/) |
| 11 | [`exercicio-11-autogen-research`](exercicio-11-autogen-research/) |
| 12 | [`exercicio-12-semantic-kernel-office`](exercicio-12-semantic-kernel-office/) |
| 13 | [`exercicio-13-dspy-optimizer`](exercicio-13-dspy-optimizer/) |
| 14 | [`exercicio-14-tutorgraph`](exercicio-14-tutorgraph/) |
| 15 | [`exercicio-15-auditoriagraph`](exercicio-15-auditoriagraph/) |
| 16 | [`exercicio-16-observaai`](exercicio-16-observaai/) |
| 17 | [`exercicio-17-localbot`](exercicio-17-localbot/) |
| 18 | [`exercicio-18-api-agent-factory`](exercicio-18-api-agent-factory/) |
| 19 | [`exercicio-19-interface-agent-studio`](exercicio-19-interface-agent-studio/) |
| 20 | [`exercicio-20-empresa-autonoma-integrada`](exercicio-20-empresa-autonoma-integrada/) |

## Variáveis de ambiente

O Compose Jupyter usa **`env_file: ../../.env`** (raiz do repositório). Monte também essa raiz para o ficheiro existir dentro do contentor.

## Biblioteca `lib_docker_empresas.sh`

Antes de subir um serviço, faz `docker compose down` nas **outras** pastas `exercicio-*`, tanto para **`docker-compose.yml`** como para **`docker-compose.jupyter.yml`**.

## Modo API / Streamlit *(opcional)*

| Pasta | Script extra |
| ----- | ------------- |
| Todas exceto 02 | `./run_api.sh` — `docker-compose.yml` (FastAPI esqueleto ou app completa no ex. 01). |
| `exercicio-02-atendimento-360` | `./run_streamlit.sh` — interface Streamlit (`docker-compose.yml`). |

## Estrutura por exercício

- `Dockerfile.jupyter` + `docker-compose.jupyter.yml` — ambiente notebook.
- `run.sh` → `run_jupyter.sh`
- `exercicio_NN_sem_ecra.ipynb` — TRABALHO principal.
- `Dockerfile` + `docker-compose.yml` — opcional (API/UI).

Os exercícios **03 a 20** mantêm esqueleto em `app/main.py`; o desenvolvimento principal está no **notebook** e em **`docs/*.md`** (explicações detalhadas).

**Convenção didática:** nos cadernos `exercicio_NN_sem_ecra.ipynb` evita-se `from app…` — o código LangChain / Pydantic / orquestrações relevantes fica **nas células**, com texto explicativo. A pasta `app/` **espelha** a mesma lógica para **FastAPI** / Docker API (código modular para produção ou para seguir no IDE).

**Exercícios 01 e 02:** o **01** segue o mesmo padrão de notebook inline + `app/`; o **02** usa sobretudo **Streamlit** opcional (`./run_streamlit.sh`) — ver README dentro da pasta.

## Regenerar / alinhar documentação e notebooks

```bash
cd empresas-automatizadas-ia/scripts
python3 generate_detalhado.py
```

O script reescreve, para **cada** pasta `exercicio-NN-*/`:

- `docs/arquitetura.md`, `explicacao_teorica.md`, `passo_a_passo.md`, `resultados.md` — texto longo e específico do exercício;
- `exercicio_NN_sem_ecra.ipynb` — código executável (LangChain + Gemini, e dependências extra nos exercícios 6, 7, 17).

**Atenção:** os notebooks **01**, **03** e **04** estão **curados à mão** (código inline, sem imports `app.*`). Se correres `generate_detalhado.py`, revê se não queres repor esses ficheiros a partir do repositório antes de commit.

Todas as `requirements.txt` incluem `langchain-core` e `langchain-google-genai` para o kernel Jupyter construir o ambiente.
