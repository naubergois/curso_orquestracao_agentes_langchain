# Exercício 02 — Atendimento 360

## Empresa simulada

A **Atendimento 360** automatiza centrais de suporte com **histórico de conversa** completo: cada contacto deve parecer contínuo, mesmo quando o cliente muda de assunto e regressa ao tema anterior.

## Problema de negócio

O cliente **reclama**, **explica**, **muda de ideia**, **volta ao assunto anterior** e espera que o sistema **lembre tudo**. Ou seja, basicamente uma **reunião de segunda-feira** — sem memória, o assistente quebra a confiança e obriga o cliente a repetir informação.

## Frameworks obrigatórios

| Framework | Uso |
|-----------|-----|
| **LangChain** | `SystemMessage`, `HumanMessage`, `AIMessage`; invocação ao Gemini. |
| **Streamlit** | Chat, botões, downloads, `st.session_state`. |
| **Docker** | `Dockerfile` + `docker-compose.yml` para subir a UI na porta **8501**. |

## Conceitos trabalhados

- Memória de conversa (lista de turnos na sessão).
- Histórico de mensagens explícito.
- Interface de chat (`st.chat_message` / `st.chat_input`).
- Estado da sessão (`st.session_state`).
- Contexto acumulado reenviado ao modelo a cada turno.

## Tarefa

Criar uma aplicação em **Streamlit** que mantenha o **histórico** da conversa e responda **considerando mensagens anteriores**, espelhando o mesmo princípio no **notebook sem ecrã** (`exercicio_02_sem_ecra.ipynb`).

## Arquitetura esperada

```text
Usuário
  ↓
Streamlit Chat
  ↓
Histórico da sessão  (st.session_state["history"])
  ↓
Prompt com memória   (LangChain: System + Human/AI alternados)
  ↓
Modelo LLM           (Gemini via GOOGLE_API_KEY)
  ↓
Resposta contextualizada
```

## Entregáveis

| Entregável | Onde |
|------------|------|
| Aplicação Streamlit | [`app/main.py`](app/main.py) |
| Histórico visual da conversa | Chat Streamlit |
| Botão para limpar memória | «Limpar conversa» |
| Docker configurado | [`Dockerfile`](Dockerfile), [`docker-compose.yml`](docker-compose.yml) |
| Documentação Markdown (memória) | [`docs/memoria_conversa.md`](docs/memoria_conversa.md), [`docs/explicacao_teorica.md`](docs/explicacao_teorica.md) |
| Notebook sem ecrã + lote + Pydantic | [`exercicio_02_sem_ecra.ipynb`](exercicio_02_sem_ecra.ipynb) |

## Funcionalidades mínimas

- Enviar mensagem.
- Visualizar histórico.
- Limpar conversa.
- Manter contexto durante a sessão (lista acumulada até limpar ou fechar o browser).

## Como o estado é armazenado (Streamlit)

- A lista de mensagens fica em **`st.session_state["history"]`**.
- Cada elemento é um dicionário **`{"role": "user" \| "assistant", "content": str}`**.
- A cada rerun do Streamlit, o servidor pode **reexecutar** o script; por isso o histórico **não** pode ficar só em variáveis locais — tem de estar em `session_state` para persistir na sessão do utilizador.
- **Limpar conversa** faz `st.session_state.history = []` — não há persistência em disco por defeito (ao fechar o separador, perde-se o histórico).
- Os botões **Exportar .txt / .json** geram ficheiros **no cliente** (download), sem gravar automaticamente no servidor.

## Como executar

**Sem ecrã (predefinição do curso — Jupyter):**

```bash
./run.sh
```

Abra `exercicio_02_sem_ecra.ipynb` no Jupyter servido pelo Docker.

**Com ecrã (Streamlit):**

```bash
./run_streamlit.sh
```

Ou em primeiro plano: `./run_streamlit.sh --fg` → `http://localhost:8501`.

Variáveis: `.env` na **raiz do repositório do curso** (`../../.env` a partir desta pasta). Ver [.env.example](.env.example).

## Exemplo de conversa

```text
Usuário: Meu nome é João.
Assistente: Certo, João. Como posso ajudar?

Usuário: Qual é meu nome?
Assistente: Seu nome é João.
```

(O comportamento exato depende do modelo e do prompt; o Histórico garante que o nome foi enviado nos turnos anteriores.)

## Desafio extra

- Exportar o histórico em **`.txt`** ou **`.json`** — implementado em [`app/main.py`](app/main.py).

## Notebook — conversas em lote e «agente» de extração

O notebook gera **várias conversas simuladas** (roteiros realistas), grava JSON em `app/data/generated/` e executa uma **cadeia de extração estruturada** (LangChain `with_structured_output` + **Pydantic**) para produzir **relatórios** agregados em Markdown. Depois constrói um **DataFrame** (CSV/Parquet) com os campos extraídos, **gráficos consolidados** (urgência, sentimento, churn) e uma **projeção ilustrativa** de volume por urgência (cenário com crescimento por período). Isto simula análise de qualidade / BI sobre tickets sem precisar da UI.

## Documentação adicional

- [`docs/arquitetura.md`](docs/arquitetura.md)
- [`docs/passo_a_passo.md`](docs/passo_a_passo.md)
- [`docs/memoria_conversa.md`](docs/memoria_conversa.md)

Regenerar textos auxiliares do monorepo: `python3 scripts/generate_detalhado.py` em `empresas-automatizadas-ia` (se aplicável).

## Possíveis melhorias

Persistência em disco por utilizador, truncagem por tokens, autenticação simples, testes de regressão sobre exportações JSON.

## 13. Testes automatizados

Os testes do monorepo vivem na raiz [`empresas-automatizadas-ia/tests/`](../tests/) e validam sobretudo **`GET /health`** desta API (quando existe FastAPI em `app/main.py`).

```bash
cd ..    # raiz `empresas-automatizadas-ia/` (pasta que contém `tests/` e `scripts/`)
pip install -r requirements-dev.txt
./scripts/install_test_deps.sh   # ou apenas: pip install -r requirements.txt (nesta pasta)
pytest tests -m "not integration"
```

- **Integração** (Gemini real): `pytest tests -m integration` — requer `GOOGLE_API_KEY`.

Guia completo: [`docs/GUIA_TESTES.md`](../docs/GUIA_TESTES.md).

### Troubleshooting

| Sintoma | O que verificar |
|--------|------------------|
| `ModuleNotFoundError` | Instalar o `requirements.txt` **desta** pasta; para a suíte inteira usar `./scripts/install_test_deps.sh`. |
| Conflitos de versão entre empresas | Usar um **venv por exercício** ou correr testes dentro do **Dockerfile** desse exercício. |
| Ex. 07 — `/buscar` falha | Criar o índice FAISS com `scripts/criar_indice.py` antes de testes que chamem `/buscar`. |
| Ex. 09 / LangGraph | Manter `langgraph>=0.2,<0.3` com `langchain-core` 0.3.x (ver `GUIA_TESTES.md`). |
