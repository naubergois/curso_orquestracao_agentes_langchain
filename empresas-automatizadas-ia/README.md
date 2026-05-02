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

## Catálogo das empresas e exercícios *(baseline)*

Cada linha corresponde a uma **empresa simulada** do curso: problema de negócio, stack técnica principal e pasta do código. Para documentação passo a passo, variáveis `.env` e critérios de avaliação, abre o **`README.md`** dentro da pasta.

| # | Empresa simulada | Pasta | Problema / foco | Frameworks & entregáveis principais |
|---|------------------|-------|-----------------|--------------------------------------|
| 01 | **PromptLab** | [`exercicio-01-promptlab`](exercicio-01-promptlab/) | Experimentação com perfis de sistema e estilos de resposta | LangChain, Pydantic, FastAPI; perfis de prompt e encadeamentos |
| 02 | **Atendimento 360** | [`exercicio-02-atendimento-360`](exercicio-02-atendimento-360/) | Suporte com **memória de conversa** na sessão | Streamlit, LangChain, Gemini; histórico exportável |
| 03 | **EduPrompt** | [`exercicio-03-eduprompt`](exercicio-03-eduprompt/) | Aprendizagem guiada (níveis, exemplos pedagógicos) | LangChain, FastAPI; prompts educativos estruturados |
| 04 | **Few-shot Marketing** | [`exercicio-04-fewshot-marketing`](exercicio-04-fewshot-marketing/) | Campanhas com **few-shot** e estilos de marca | LangChain, Instructor/Pydantic, FastAPI; geração de campanhas |
| 05 | **Parser Jurídico** | [`exercicio-05-parser-juridico`](exercicio-05-parser-juridico/) | Extrair estrutura de pedidos jurídicos em texto livre | LangChain, schemas Pydantic; API de análise |
| 06 | **RAG Jurídico** | [`exercicio-06-rag-juridico`](exercicio-06-rag-juridico/) | Respostas **com fontes** sobre documentos internos fictícios | LlamaIndex, ChromaDB, Gemini (embeddings + LLM); API RAG |
| 07 | **Busca Semântica Ltda.** | [`exercicio-07-busca-semantica`](exercicio-07-busca-semantica/) | Falha da keyword quando o utilizador usa sinónimos | **FAISS**, Hugging Face Transformers, Docker; índice + top‑k semântico |
| 08 | **GovBot Cidadão** | [`exercicio-08-govbot`](exercicio-08-govbot/) | Perguntas sobre IPTU, protocolos, serviços urbanos *(fictício)* | **Haystack**, **Qdrant**, Gemini; chat com classificação da demanda |
| 09 | **HelpDesk Agent** | [`exercicio-09-helpdesk-agent`](exercicio-09-helpdesk-agent/) | Tickets vagos (“não funciona”) precisam de **tools** | LangGraph, LangChain, FastAPI; abrir/consultar/classificar (+ prioridade) |
| 10 | **CrewFinance** | [`exercicio-10-crewfinance`](exercicio-10-crewfinance/) | Relatório financeiro com **papéis** (analista, crítico, redator…) | **CrewAI**, Pydantic, Gemini via LiteLLM; `POST /relatorio` |
| 11 | **AutoGen Research Lab** | [`exercicio-11-autogen-research`](exercicio-11-autogen-research/) | Relatório melhorado por **debate** entre agentes | **AutoGen** AgentChat, Gemini OpenAI-compat; `POST /debate` |
| 12 | **Semantic Kernel Office** | [`exercicio-12-semantic-kernel-office`](exercicio-12-semantic-kernel-office/) | Resumo, e-mail, tarefas, reunião (skill composta) | **Semantic Kernel**, Gemini; `POST /executar` |
| 13 | **DSPy Optimizer** | [`exercicio-13-dspy-optimizer`](exercicio-13-dspy-optimizer/) | Comparar versões de prompt com **métrica** | **DSPy**, FastAPI; `POST /avaliar`, dataset em `data/` |
| 14 | **TutorGraph** | [`exercicio-14-tutorgraph`](exercicio-14-tutorgraph/) | Tutor adaptativo em **grafo** (diagnosticar → … → revisar) | **LangGraph**, Pydantic (API), Gemini; `POST /sessao` |
| 15 | **AuditoriaGraph** | [`exercicio-15-auditoriagraph`](exercicio-15-auditoriagraph/) | Achados com ramos por **risco** (baixo/médio/alto) | LangGraph, **LangSmith** (env), Gemini; `POST /analisar` |
| 16 | **ObservaAI** | [`exercicio-16-observaai`](exercicio-16-observaai/) | Comparar prompts com **latência, erro, custo estimado** | LangChain, **MLflow** (ficheiro), Streamlit opcional; `POST /experimentos` |
| 17 | **LocalBot** | [`exercicio-17-localbot`](exercicio-17-localbot/) | IA **local** (privacidade) vs nuvem | **Ollama**, LangChain, FastAPI; `/chat`, `/chat/compare` |
| 18 | **API Agent Factory** | [`exercicio-18-api-agent-factory`](exercicio-18-api-agent-factory/) | Integração por **REST** (`/chat`, `/classificar`, `/resumir`) | FastAPI, LangChain; Swagger; token Bearer opcional |
| 19 | **Interface Agent Studio** | [`exercicio-19-interface-agent-studio`](exercicio-19-interface-agent-studio/) | Mesmo agente em **Streamlit** e **Gradio** | Streamlit, Gradio, LangChain; compose com dois serviços |
| 20 | **Empresa Autónoma Integrada** | [`exercicio-20-empresa-autonoma-integrada`](exercicio-20-empresa-autonoma-integrada/) | Projeto **integrador**: classificar → RAG → especialista → revisor → relatório | LangGraph, Chroma, Gemini (+ embeddings), Streamlit + API; `POST /pipeline` |

### Legenda rápida

- **Notebook principal:** `exercicio_NN_sem_ecra.ipynb` em cada pasta.
- **API modular:** `app/main.py` (FastAPI), exceto **02** (Streamlit em `app/main.py`) e **19** (Streamlit/Gradio na raiz da pasta).
- **Testes:** na raiz `empresas-automatizadas-ia/`, ver secção [Testes automatizados](#testes-automatizados-pytest) e [`docs/GUIA_TESTES.md`](docs/GUIA_TESTES.md).

## Índice rápido *(só pastas)*

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
| Maioria dos exercícios | `./run_api.sh` — `docker-compose.yml` com **FastAPI** quando aplicável. |
| `exercicio-02-atendimento-360` | `./run_streamlit.sh` — **Streamlit** (`docker-compose.yml`). |
| `exercicio-19-interface-agent-studio` | `docker compose up` — **Streamlit + Gradio** (sem `app` FastAPI único). |

## Testes automatizados *(pytest)*

Na pasta **`empresas-automatizadas-ia/`** (raiz do monorepo de empresas):

```bash
pip install -r requirements-dev.txt
./scripts/install_test_deps.sh    # instala todos os exercicio-*/requirements.txt
pytest tests -m "not integration"
```

- **Smoke:** `GET /health` em todas as APIs FastAPI + testes pontuais (ex. 02, 07, 13, 19).
- **Integração** (opcional, custo API): `pytest tests -m integration` com `GOOGLE_API_KEY` definida.

Documentação detalhada: [`docs/GUIA_TESTES.md`](docs/GUIA_TESTES.md).

## Estrutura por exercício

- `Dockerfile.jupyter` + `docker-compose.jupyter.yml` — ambiente notebook.
- `run.sh` → `run_jupyter.sh`
- `exercicio_NN_sem_ecra.ipynb` — trabalho guiado no Jupyter.
- `Dockerfile` + `docker-compose.yml` — API ou UI em contentor (quando existir).
- `app/` — código modular espelhando a lógica do notebook (FastAPI, RAG, agentes, etc.), conforme o exercício.

Muitos exercícios têm **README.md** com as 12 secções do curso **mais a secção 13 (testes)**. O notebook continua a ser o ponto de entrada didático; a pasta `app/` serve para execução tipo produção e para os testes automatizados importarem o mesmo código.

**Convenção didática:** nos cadernos `exercicio_NN_sem_ecra.ipynb` o código pode estar **inline** nas células; a pasta `app/` mantém módulos alinhados para Docker e IDE.

**Exercício 02:** `app/main.py` é a app **Streamlit** (não FastAPI). **Exercício 19:** interfaces Streamlit/Gradio + `app/agent_shared.py`.

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
