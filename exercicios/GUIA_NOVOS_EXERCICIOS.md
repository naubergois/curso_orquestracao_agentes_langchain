# Guia: novos exercícios, Docker e padrões de qualidade

Este documento serve para **pessoas** e para **agentes / IDEs com IA** que criem ou alterem exercícios no repositório. Segue a estrutura **já adoptada** em `exercicios/` (ex.: `00_alo_mundo`, `01_…_com_ecra`, `01_…_sem_ecra`, `03_calculadora`, `03_calculadora_sem_ecra`, `05_prompt_templates_lcel_sem_ecra`, `06_memoria_langchain_sem_ecra`, `07_precos_clima_cotacao`, `07_precos_clima_cotacao_sem_ecra`, `08_chains_complexas_sem_ecra`, `09_rag_juridico_*`, `10_triagem_imagens_patologia_*`, `12_pdf_chunks_split_sem_ecra`, `13_agente_pdf_sem_ecra`).

---

## 1. Princípios

- **Um conceito por exercício** — código mínimo; sem refactors ou funcionalidades não pedidas noutros ficheiros.
- **Português** — cabeçalhos, mensagens de erro úteis ao aluno, comentários só onde clarificam decisão de desenho (evitar ruído).
- **Gemini** — usar **sempre modelos da família 2.x** (predefinição típica: `gemini-2.0-flash`). Não documentar nem predefinir `gemini-1.5*`. Se `GEMINI_MODEL` vier com `1.5`, o código pode avisar e corrigir para 2.x (ver exercícios existentes).
- **Chave API** — `GOOGLE_API_KEY` ou `GEMINI_API_KEY`; ficheiro `.env` na **raiz do repositório** (nunca commitar valores reais).
- **Segurança local** — Jupyter sem token/senha é aceitável **só em localhost**; não expor portas 8888/8501 à Internet sem autenticação.

---

## 2. Nomenclatura e pastas

| Padrão | Uso |
|--------|-----|
| `NN_descricao_…` | `NN` = número com zero à esquerda (`00`, `01`, …). |
| `…_com_ecra` | Streamlit (ou outra UI) + Docker `docker-compose.yml` + `Dockerfile` “app”. |
| `…_sem_ecra` | Jupyter Lab + `docker-compose.jupyter.yml` + `Dockerfile.jupyter`. |
| `00_…` | Exercício de entrada: pode ter `main.py` + Jupyter + compose “app” para uma execução (`run.sh --once`). |

Copiar uma pasta existente **análoga** (ex.: `03_calculadora` para novo Streamlit) e renomear costuma ser mais seguro do que começar do zero.

---

## 3. Variáveis de ambiente (`.env` na raiz)

- **`GEMINI_MODEL`** — exercícios que usam o mesmo modelo “genérico” (01 com ecrã, 03, 00, etc.).
- **`GEMINI_MODEL_EX02`** — só o exercício 02 (com e sem ecrã podem usar a mesma variável para não colidir com o 01).
- **`GEMINI_MODEL_EX05`** — opcional no exercício 05 (LCEL); se vazio, usa-se `GEMINI_MODEL`.
- **`GEMINI_MODEL_EX06`** — opcional no exercício 06 (memória / histórico); se vazio, usa-se `GEMINI_MODEL`.
- **`GEMINI_MODEL_EX07`** — opcional no exercício 07 (preços / clima / câmbio); se vazio, usa-se `GEMINI_MODEL`.
- **`GEMINI_MODEL_EX08`** — opcional no exercício 08 (cadeias LCEL compostas); se vazio, usa-se `GEMINI_MODEL`.
- **`GEMINI_MODEL_EX09`** — opcional no exercício 09 (RAG jurídico / Chroma); se vazio, usa-se `GEMINI_MODEL`.
- **`GEMINI_MODEL_EX10`** — opcional no exercício 10 (triagem de imagens + MongoDB); se vazio, usa-se `GEMINI_MODEL`.
- **`GEMINI_MODEL_EX13`** — opcional no exercício 13 (agente sobre PDFs chunkados); se vazio, usa-se `GEMINI_MODEL`.
- **`GEMINI_MODEL_EX23`** — opcional no exercício 23 (laudos + Chroma + Streamlit); se vazio, usa-se `GEMINI_MODEL`.
- Novo exercício com modelo **dedicado**: definir nome claro (`GEMINI_MODEL_EXNN` ou prefixo do tema) e **documentar em `.env.example`** com comentário e caminho da pasta.
- Opcionais partilhados: `GEMINI_RETRY_ATTEMPTS`, `GEMINI_RETRY_DELAY_SEC`.

Actualizar **sempre** `.env.example` quando um exercício novo introduzir variáveis.

---

## 4. Docker — padrão “com ecrã” (Streamlit)

Ficheiros típicos em `exercicios/NN_tema_com_ecra/`:

| Ficheiro | Função |
|----------|--------|
| `Dockerfile` | `FROM python:3.12-slim`; `ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1`; `pip install --upgrade pip` + `requirements.txt`; `COPY` de `agent.py` + `streamlit_app.py`; `EXPOSE 8501`; `CMD streamlit run …`. |
| `docker-compose.yml` | `name: curso-exNN-…` (único); serviço `streamlit`; `ports` `${STREAMLIT_PORT:-8501}:8501`; `env_file: ../../.env`; `volumes: ../../.env:/app/.env:ro`; `environment`: `GOOGLE_API_KEY`, `GEMINI_API_KEY`, modelo com default **2.x**, `PYTHONUNBUFFERED: "1"`. |
| `.dockerignore` | `__pycache__`, `*.pyc`, `.venv`, `venv`, `.git`, `.env`. |
| `requirements.txt` | `streamlit`, `python-dotenv`, `langchain-core`, `langchain-google-genai` (intervalos de versão como nos existentes). |
| `agent.py` | Lógica LangChain / Gemini; `load_dotenv` subindo pastas até encontrar `.env`. |
| `streamlit_app.py` | **Só UI**; importa funções de `agent.py`. |
| `run.sh` / `run.ps1` | Predefinição **Docker** em segundo plano; `--local` ou `-Local` para venv na raiz do repo; alinhar com `02_nerd_sarcastico_com_ecra` / `03_calculadora`. |
| `run_docker.sh` / `.ps1` / `.cmd` | Presente no 01; predefinição segundo plano; `--fg` primeiro plano. |

### Bloco típico no serviço Compose

```yaml
env_file:
  - ../../.env
volumes:
  - ../../.env:/app/.env:ro
environment:
  GOOGLE_API_KEY: ${GOOGLE_API_KEY:-}
  GEMINI_API_KEY: ${GEMINI_API_KEY:-}
  GEMINI_MODEL: ${GEMINI_MODEL:-gemini-2.0-flash}
  PYTHONUNBUFFERED: "1"
```

(Ajustar `GEMINI_MODEL_EX02` ou outra variável se for o caso.)

---

## 5. Docker — padrão “sem ecrã” (Jupyter)

Pasta `exercicios/NN_tema_sem_ecra/`:

| Ficheiro | Função |
|----------|--------|
| `Dockerfile.jupyter` | `FROM quay.io/jupyter/minimal-notebook:latest`; `USER root`; `COPY requirements.txt` para `/tmp/requirements-….txt`; `pip install --upgrade pip` + requirements; `fix-permissions`; `USER ${NB_UID}`. **Sem** `streamlit` nos requirements — só o necessário para o caderno (como em `00_alo_mundo/requirements.txt`). |
| `docker-compose.jupyter.yml` | `name: curso-exNN-sem-jupyter` (único); `build.dockerfile: Dockerfile.jupyter`; `ports` `${JUPYTER_PORT:-8888}:8888`; `env_file: ../../.env`; `environment`: chaves Google, variável(s) de modelo **2.x**, `PYTHONUNBUFFERED`, `JUPYTER_TOKEN: ""`; **volume do repo**: `../../:/home/jovyan/work/repo:rw` e `../../.env:/home/jovyan/work/repo/.env:ro`; `working_dir: /home/jovyan/work/repo/exercicios/NN_tema_sem_ecra`; `command` com `start-notebook.sh` e token/password vazios + `ip=0.0.0.0`. |
| `run_jupyter.sh` / `.ps1` / `.cmd` | `source ../lib_docker_exercicios.sh` + `parar_outros_exercicios_docker`; variável opcional `EXNN_NOTEBOOK=…ipynb`; URL do Lab a apontar para o caderno. |
| `run.sh` / `run.ps1` / `run.cmd` | Delegar para `run_jupyter.sh` / `run_jupyter.ps1`. |
| `exercicio_N_sem_ecra.ipynb` | **Código autocontido** — **não** importar `agent.py` do repo; exemplos mínimos em poucas células. |

**Nota:** Os `.ipynb` estão no volume montado — actualizar o caderno **não exige** rebuild da imagem; só rebuild se mudar `requirements.txt` ou `Dockerfile.jupyter`.

---

## 6. Export estático: `CODIGO_COMPLETO.txt`

Cada pasta de exercício `exercicios/NN_*` (regex: `^\d\d_.+`) deve incluir **`CODIGO_COMPLETO.txt`** na **raiz dessa pasta**: um único `.txt` com o código do exercício para leitura offline, impressão ou revisão sem abrir o IDE/notebook.

| Regra | Detalhe |
|--------|---------|
| Conteúdo | `requirements.txt` (se existir); todos os `*.py` **directamente** nessa pasta (ordem: `main.py`, `agent.py`, `streamlit_app.py`, depois os restantes por nome); em seguida cada `*.ipynb` no mesmo nível — células **markdown** como linhas comentadas com `# `, células **código** em texto puro. |
| Geração | Ficheiro **gerado** — não editar à mão. Na **raiz do repositório:** `python exercicios/gerar_codigo_completo_txt.py` |
| O que fica de fora | Scripts `run_*`, Dockerfiles, composes e ficheiros em subpastas (ex.: `.ipynb_checkpoints`) não entram no export. |
| Novos exercícios | Após criar ou alterar `.py` / `.ipynb` ou `requirements.txt` do exercício, voltar a correr o comando e **commitar** o `CODIGO_COMPLETO.txt` actualizado junto com as alterações. |
| Pasta extra | `rag_auditoria_rostos_sem_ecra` (lista `EXTRA_CODIGO_COMPLETO_DIRS` em `gerar_codigo_completo_txt.py`) gera também **`CODIGO_COMPLETO.md`** junto do `.txt`. |

---

## 7. Biblioteca partilhada Docker

- `exercicios/lib_docker_exercicios.sh` e `lib_docker_exercicios.ps1` — função que **para outros** stacks em `exercicios/*/`: qualquer pasta com `docker-compose.yml` **ou** `docker-compose.jupyter.yml`.
- Os scripts `run_*` do novo exercício devem **chamar** essa função antes de subir, para libertar portas e evitar conflitos de projecto Compose.

---

## 8. Scripts de manutenção (actualizar ao adicionar stacks)

| Script | Acção |
|--------|--------|
| `exercicios/rebuild_all_docker.sh` | Adicionar **uma chamada** `build_stack pasta ficheiro.yml` por cada compose que constrói imagem. |
| `exercicios/rebuild_all_docker.ps1` | Duplicar entradas na tabela `$stacks`. |
| `exercicios/update_notebooks.py` | Percorre `exercicios/**/*.ipynb`; novos cadernos incluem-se **automaticamente** ao limpar outputs. |
| `exercicios/gerar_codigo_completo_txt.py` | Regenera `CODIGO_COMPLETO.txt` em cada `exercicios/NN_*`. Correr após mudanças em código de exercícios. |

---

## 9. Qualidade de código e arquitectura

- **Com ecrã:** `streamlit_app.py` fino; lógica em `agent.py`.
- **Sem ecrã:** lógica visível no notebook; fluxo legível de cima a baixo.
- **Retries 429:** seguir o padrão `GEMINI_RETRY_*` já usado nos `agent.py` que chamam a API.
- **Mensagens de erro:** indicar o que falta (chave, modelo) e, quando útil, link à documentação oficial de limites Google.
- **Estilo:** alinhar imports, `pathlib` e type hints aos ficheiros vizinhos.
- **Commits:** diffs pequenos e focados; não misturar exercício novo com refactors não relacionados.

### 9.1 Agentes lentos — progresso e custo (boas práticas)

Quando o exercício usa **LangGraph / ferramentas + LLM**, cada turno pode demorar e custar vários tokens. Preferir:

| Prática | Motivo |
|--------|--------|
| **`graph.stream(..., stream_mode="updates")`** na UI | Permite actualizar `st.progress` (ou `tqdm` no Jupyter) a cada passo do grafo; o utilizador vê que o processo avança. |
| **Um registo / uma entidade por pedido** | Evita «lista todos e analisa todos» numa só mensagem: são mais rodadas modelo↔tool e respostas mais longas. Usar **seletor** (dropdown), **navegação página a página**, ou **filas** explícitas no chat. |
| **Prompt e system message alinhados** | Instruir o modelo a **não** fundir múltiplos casos numa resposta salvo o utilizador pedir explicitamente (ex.: «cada paciente», «todos»). |
| **`st.status` + barra** (Streamlit) | Combina contexto («a trabalhar») com percentagem ou número de passos; no fim, `state="complete"` ou `error`. |
| **Erro 429 / RESOURCE_EXHAUSTED** | Limite da API Google (quota), não necessariamente bug do código. Aumentar `GEMINI_RETRY_ATTEMPTS`, `GEMINI_RETRY_DELAY_SEC`, `GEMINI_RETRY_MAX_SLEEP_SEC`; espaçar execuções; preferir um registo por pedido; ver [limites Gemini](https://ai.google.dev/gemini-api/docs/rate-limits). |

**Referência no repositório:** `exercicios/04_fatores_risco_pacientes/` (Streamlit + sidebar «um paciente de cada vez» + progresso por updates; **LLM: DeepSeek** via `DEEPSEEK_API_KEY`).

### 9.2 *Fallback* de modelos (Gemini e DeepSeek, a partir do exercício 5)

Objetivo: quando o primário falha com **nome inválido**, **404**, **403**, **429** / **`RESOURCE_EXHAUSTED`**, ou erros típicos de «modelo não disponível», tentar **outro identificador** na mesma API (outro *bucket* de quota ou outro SKU).

| Peça | Função |
|------|--------|
| **`make_gemini_chat_with_runtime_fallback` / `make_deepseek_chat_with_runtime_fallback`** | Empilham modelos com **`Runnable.with_fallbacks`** do LangChain: **cada** `invoke` tenta o seguinte se o anterior lançar excepção (incl. **429**). O exercício 5 usa o primeiro; o exercício 4 (DeepSeek) também. |
| **`GEMINI_MODEL_FALLBACKS`** | Lista CSV opcional (ex.: `gemini-2.5-flash,gemini-2.0-flash-lite`) **depois** do primário (`GEMINI_MODEL_EX05` ou `GEMINI_MODEL`). |
| **`DEEPSEEK_MODEL_FALLBACKS`** | Idem para DeepSeek (ex.: `deepseek-reasoner,deepseek-chat`). |
| **`LLM_FALLBACK_SKIP_SMOKE_TEST`** | Se `1` / `true` / `yes`, **não** é feito o `invoke` curto de teste por modelo — usa logo o primeiro nome da lista (poupa chamadas; útil se já validou os nomes). |

- **Listar nomes válidos:** o exercício 5 inclui células que chamam a API (Gemini: `client.models.list()`; DeepSeek: `GET …/v1/models`). Use isso para preencher `.env` e reduzir `ChatGoogleGenerativeAIError` / erros OpenAI-compatíveis por modelo inexistente.
- **DeepSeek no Streamlit (ex. 4):** o `Dockerfile` usa **contexto de build `exercicios/`** para copiar `lib_llm_fallback.py` para a imagem junto de `agent.py`.
- **Jupyter:** `Path.cwd().parent` aponta para `exercicios/` — import de `lib_llm_fallback` após `sys.path.insert`.
- **429 Google:** mudar de modelo **pode** ajudar; se todos falharem, o problema é quota global — espere e consulte [limites Gemini](https://ai.google.dev/gemini-api/docs/rate-limits). Para DeepSeek, ver a documentação da plataforma.

## 10. Checklist — novo par de exercícios (com + sem ecrã)

- [ ] Pastas `NN_…_com_ecra` e `NN_…_sem_ecra` com nomes consistentes.
- [ ] `docker-compose.yml` e `docker-compose.jupyter.yml` com `name:` únicos no repositório.
- [ ] Variáveis `environment` + `../../.env` montado em `:ro`.
- [ ] Modelos **Gemini 2.x** nos defaults; `.env.example` actualizado.
- [ ] `agent.py` + `streamlit` só em `…_com_ecra`; notebook autocontido em `…_sem_ecra`.
- [ ] `run.sh` com predefinição Docker (Streamlit em segundo plano; Jupyter via `run_jupyter`).
- [ ] `lib_docker` invocado nos scripts de arranque.
- [ ] `rebuild_all_docker.sh` / `.ps1` actualizados.
- [ ] `chmod +x` em `run.sh`, `run_jupyter.sh`, `rebuild_all_docker.sh`, `update_notebooks.sh` onde aplicável.
- [ ] Opcional: `./update_notebooks.sh` antes de commit para notebooks sem outputs gravados.
- [ ] `python exercicios/gerar_codigo_completo_txt.py` e `CODIGO_COMPLETO.txt` actualizado em **cada** pasta `NN_*` afectada.

---

## 11. Checklist — só “com ecrã” ou só “sem ecrã”

- **Só Streamlit:** omitir pasta `sem_ecra`.
- **Só Jupyter:** omitir `…_com_ecra`; documentar no README ou neste guia se for caso especial (como o 00).

---

## 12. Referência rápida de exemplos no repositório

| Caso | Com ecrã | Sem ecrã |
|------|----------|----------|
| Chat com histórico | `01_alo_mundo_com_ecra` | `01_alo_mundo_sem_ecra` |
| Persona fixa, sem histórico no modelo | `02_nerd_sarcastico_com_ecra` | `02_nerd_sarcastico_sem_ecra` |
| LangGraph / tools | `03_calculadora` | `03_calculadora_sem_ecra` |
| Agente + DB / muitos registos (progresso, um-a-um); LLM **DeepSeek** | `04_fatores_risco_pacientes` | `04_fatores_risco_pacientes_sem_ecra` |
| LCEL + *prompt templates* (só Jupyter) | — | `05_prompt_templates_lcel_sem_ecra` |
| Entry `main.py` + Jupyter | `00_alo_mundo` | `exercicio_0_sem_ecra.ipynb` |

---

## 13. Instruções para agentes de IA

- **Não** criar `.md` extra **por exercício** sem pedido explícito do utilizador; usar este guia como referência central.
- **Não** duplicar lógica entre `agent.py` e notebook em exercícios **sem ecrã**; o caderno é a fonte de verdade.
- Após editar composes, validar: `docker compose -f <ficheiro> config`.
- Ao adicionar stacks novas, **actualizar** `rebuild_all_docker.sh` e `rebuild_all_docker.ps1`.
- Manter **sempre** a política **Gemini 2.x** nos defaults e na documentação.

---

*Documento alinhado à estrutura do repositório `curso_orquestracao_agentes_langchain` (Compose com `name:`, volumes Jupyter no repo, variáveis partilhadas na raiz).*
