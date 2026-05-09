# Exercícios (LangChain)

Pastas numeradas com exercícios **com ecrã** (`…_com_ecra`, Streamlit + Docker) e **sem ecrã** (`…_sem_ecra`, Jupyter Lab + Docker), mais utilitários partilhados.

Para um **percurso paralelo** com 20 cenários de empresa (mesmo `.env` na raiz, Jupyter por defeito), vê [`../empresas-automatizadas-ia/README.md`](../empresas-automatizadas-ia/README.md).

- **Gemini (Google AI):** exercícios **00–03** e **05–11** e **13** e **17–18** (excepto o **04** e o **12**) — variável **`GOOGLE_API_KEY`** e, consoante o exercício, **`GEMINI_MODEL`** ou `GEMINI_MODEL_EXNN` (ver `.env.example`).
- **DeepSeek:** exercício **04** — **`DEEPSEEK_API_KEY`**, `DEEPSEEK_MODEL`, `DEEPSEEK_MODEL_FALLBACKS` (CSV, opcional), `DEEPSEEK_API_BASE`; o compose define `DATABASE_URL` para o PostgreSQL no contentor.
- **Ex. 05 (só Jupyter):** LCEL e *prompt templates* — opcional **`GEMINI_MODEL_EX05`**, senão **`GEMINI_MODEL`**; **`GEMINI_MODEL_FALLBACKS`** opcional (ver GUIA §9.2).
- **Ex. 06 (só Jupyter):** memória / histórico — `RunnableWithMessageHistory`, lista manual, `trim_messages`; opcional **`GEMINI_MODEL_EX06`**.
- **Ex. 08 (só Jupyter):** LCEL avançado — `RunnableParallel`, `RunnablePassthrough.assign`, `RunnableBranch`, `RunnableLambda`, `itemgetter`; opcional **`GEMINI_MODEL_EX08`**.
- **Ex. 09:** **RAG** sobre PDFs pedagógicos com **Chroma** (vários embeddings: FastEmbed local + **Gemini**); **PostgreSQL** com processos fictícios e **RAG híbrido** (SQL estruturado + excertos PDF). Jupyter inclui serviço `db` e `DATABASE_URL`.
- **Ex. 10:** **Triagem** com **DermaMNIST** (MedMNIST), classificador **Random Forest** (sklearn sobre pixeis 28×28), **MongoDB** e agente ReAct; variáveis `GEMINI_MODEL_EX10`, `MONGODB_URI`, etc. (ver `.env.example`).
- **Ex. 11:** **Pydantic v2** — modelos, validadores, nested models, JSON Schema; secção opcional **Gemini** com `with_structured_output`; opcional **`GEMINI_MODEL_EX11`** (ver `.env.example`).
- **Ex. 12 (só Jupyter):** **PDF** + **pypdf** + *text splitters* — **sem LLM** (não precisa de `GOOGLE_API_KEY`).
- **Ex. 13 (só Jupyter):** agente **ReAct** sobre chunks em RAM; opcional **`GEMINI_MODEL_EX13`**.

## Início rápido

1. Copiar `.env.example` para **`.env` na raiz do repositório** e definir as chaves necessárias ao exercício que fores correr.
2. Entrar na pasta do exercício e seguir o `run.sh` / `run.ps1` / `run.cmd` (predefinição: **Docker**).

## Documentação completa

**[GUIA_NOVOS_EXERCICIOS.md](./GUIA_NOVOS_EXERCICIOS.md)** — como criar Docker para novos exercícios, convenções de pastas, variáveis de ambiente, checklists e padrões de qualidade (para humanos e para agentes de IA).

## Scripts úteis (nesta pasta)

| Script | Descrição |
|--------|-----------|
| `lib_llm_fallback.py` | *Fallback* de modelos (Gemini / DeepSeek) e listagem via API — GUIA §9.2. |
| `rebuild_all_docker.sh` / `.ps1` | Reconstrói as imagens de **todos** os composes dos exercícios (`build --pull`). |
| `update_notebooks.sh` / `.ps1` | Limpa **outputs** dos `.ipynb` em `exercicios/` (útil antes de commit). |
| `lib_docker_exercicios.sh` / `.ps1` | Usado pelos `run_*` — para stacks paralelos não ficarem a competir pela mesma porta. |
| `gerar_codigo_completo_txt.py` | Gera `CODIGO_COMPLETO.txt` a partir dos cadernos `…_sem_ecra`. |
| `_sync_nb_ex07.py` | Actualiza `07_precos_clima_cotacao_sem_ecra/exercicio_7_sem_ecra.ipynb` a partir de `07_precos_clima_cotacao/agent.py` (após editar o agente). |

## O que faz cada exercício

| # | Pasta(s) | O que faz |
|---|----------|-----------|
| **00** | `00_alo_mundo` | **Primeiro contacto** com o modelo (Gemini): mensagem simples via API. Predefinição: **Jupyter**; opcional **`main.py`** com `./run.sh --once`. |
| **01** | `01_alo_mundo_com_ecra` | **Chat na UI** (Streamlit) com histórico de conversa na sessão. |
| | `01_alo_mundo_sem_ecra` | O mesmo conceito de **chat com histórico** no **Jupyter** (sem Streamlit). |
| **02** | `02_nerd_sarcastico_com_ecra` | **Persona** fixa com **`SystemMessage`** “nerd sarcástico”; respostas no Streamlit alinhadas com esse tom. |
| | `02_nerd_sarcastico_sem_ecra` | Mesma **persona por mensagem de sistema** em **Jupyter**. |
| **03** | `03_calculadora` | **Agente** com **ferramenta** (calculadora), **LangGraph** e UI Streamlit — o modelo decide quando invocar a tool. |
| | `03_calculadora_sem_ecra` | Mesmo **agente + ferramenta** em **Jupyter** (fluxo legível célula a célula). |
| **04** | `04_fatores_risco_pacientes` | **Agente** que lê dados **fictícios** em **PostgreSQL** (fichas de pacientes) e comenta **fatores de risco**; **DeepSeek** + Streamlit, **um paciente por pedido**, barra de progresso. |
| | `04_fatores_risco_pacientes_sem_ecra` | Mesmo **cenário BD + agente DeepSeek** no **Jupyter**; `init_db/` no Docker e recuperação de schema em volume vazio. |
| **05** | `05_prompt_templates_lcel_sem_ecra` | **LCEL**: `ChatPromptTemplate`, composição em cadeia de *runnables* (operador *pipe* entre passos), `StrOutputParser`, `partial`, `RunnablePassthrough.assign`, `RunnableParallel` — *pipelines* sem agente. **Só Jupyter.** |
| **06** | `06_memoria_langchain_sem_ecra` | **Memória / histórico**: conversa sem estado vs lista manual vs **`RunnableWithMessageHistory`**; **`trim_messages`** para limitar contexto; panorama (LangGraph, RAG). **Só Jupyter.** |
| **07** | `07_precos_clima_cotacao` | **Agente ReAct** com **treze *tools*** — preços (MLB), clima (Fortaleza), USD/BRL e EUR/BRL, Wikipédia PT, DuckDuckGo instantâneo, CEP e feriados (BrasilAPI), calculadora, data/hora por fuso, conversão °C→°F, extração de URLs, SHA-256 (padrões típicos LangChain / tutoriais). Streamlit; **Internet**. |
| | `07_precos_clima_cotacao_sem_ecra` | O mesmo conjunto de *tools* no **Jupyter** (caderno alinhado ao `agent.py`). |
| **08** | `08_chains_complexas_sem_ecra` | **Cadeias LCEL compostas:** paralelo, `assign`, ramificação condicional, `Lambda`, `itemgetter`, *pipeline* que funde vários ramos — quando usar LangGraph vs LCEL. **Só Jupyter.** |
| **09** | `09_rag_juridico_com_ecra` | **RAG jurídico (pedagógico):** PDFs (ReportLab ou agente), **Chroma** com três coleções de embeddings, chat Streamlit; opcão **híbrida** com Postgres (`docker-compose` com `db`). |
| | `09_rag_juridico_sem_ecra` | Mesmo fluxo no **Jupyter** + caderno com **LCEL explícito** e consulta SQL demonstrativa; `init_db/` para Postgres. |
| **10** | `10_triagem_imagens_patologia_com_ecra` | **Imagens** + **MongoDB** + agente **ReAct** na UI Streamlit (triagem tipo lista de espera). |
| | `10_triagem_imagens_patologia_sem_ecra` | Notebook com dataset técnico (DermaMNIST) e integração MongoDB. |
| **11** | `11_pydantic_sem_ecra` | **Pydantic** (`BaseModel`, `Field`, validadores, nested, JSON Schema) e opcional **saída estruturada** com Gemini. **Só Jupyter.** |
| **12** | `12_pdf_chunks_split_sem_ecra` | **PDF** pedagógico (ReportLab), texto com **pypdf**, **RecursiveCharacterTextSplitter** vs **CharacterTextSplitter**, overlap e **`Document`** com metadata. **Só Jupyter** (sem LLM obrigatório). |
| **13** | `13_agente_pdf_sem_ecra` | PDF + chunks em memória e **agente ReAct** (LangGraph + Gemini) com *tools* `estatisticas_corpus`, `procurar_trechos`, `ler_chunk_completo`. Opcional **`GEMINI_MODEL_EX13`**. **Só Jupyter.** |
| **17** | `17_noticias_resumo_executivo_sem_ecra` | **Pesquisa Web** (DuckDuckGo), **agente** de recolha, **Pydantic**, **indicadores** e **agente** redactor (Markdown). **Internet** + **`GOOGLE_API_KEY`**; opcional **`GEMINI_MODEL_EX17`**. **Jupyter** (`./run.sh`) e **opcional Streamlit** (`./run_streamlit.sh`, porta **8502**) que reutiliza o **agente do ex. 18** para UI/HTML. |
| **18** | `18_agente_frontend_design` | **Agente ReAct** Nielsen + *tool* **`executar_boletim_noticias_ex17`** (pipeline do ex. 17). Streamlit em **duas abas** (boletim directo + chat / HTML). *Build* Docker na **raiz do repo** (inclui `noticias_agentes.py`). **`GOOGLE_API_KEY`**, rede; opcional **`GEMINI_MODEL_EX18`** / **`GEMINI_MODEL_EX17`**. Porta **8501**. |

**Legenda:** *com ecrã* → Streamlit + `docker-compose.yml`; *sem ecrã* → Jupyter + `docker-compose.jupyter.yml` (quando existir par, o tema é o mesmo; muda só a interface).

## Exemplo isolado

Em `../exemplos/01_system_message_docker/` há um exemplo mínimo de mensagem de sistema com Docker (ver `README` ou comentários nessa pasta, se existirem).
