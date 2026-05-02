# Exercício 03 — EduPrompt Academy

## Empresa simulada

A **EduPrompt Academy** vende **trilhas educacionais personalizadas com IA**.

## Problema de negócio

**Professores** precisam gerar **explicações**, **exercícios**, **resumos** e avaliações **rapidamente**, com qualidade consistente e adaptada ao nível dos alunos.

## Frameworks obrigatórios

| Framework | Uso neste exercício |
|-----------|---------------------|
| **LangChain** | `ChatPromptTemplate`, modelo Gemini, `StrOutputParser`. |
| **LCEL** | Operador `\|` e `RunnableParallel` para compor chains reutilizáveis. |
| **Docker** | `Dockerfile` + `docker-compose.yml` (API FastAPI na porta **8000**); Jupyter em `docker-compose.jupyter.yml`. |

## Conceitos trabalhados

- **PromptTemplate** (na prática com **`ChatPromptTemplate`**, adequado a modelos de chat — ver [`docs/explicacao_teorica.md`](docs/explicacao_teorica.md)).
- **LCEL** — sequências e paralelismo.
- **Chains reutilizáveis** — definidas no [**notebook**](exercicio_03_sem_ecra.ipynb); `app/chains/` espelha para a API Docker.
- **StrOutputParser** — saída normalizada em texto.

## Tarefa

Criar **três chains**:

1. **Gerador de explicação**
2. **Gerador de exercícios**
3. **Gerador de resumo**

## Arquitetura esperada

```text
Tema informado (tema, nivel)
  ↓
PromptTemplate (ChatPromptTemplate)
  ↓
Modelo (Gemini)
  ↓
StrOutputParser
  ↓
Resposta educacional (Markdown composto no cliente/notebook/API)
```

## Entregáveis

| Entregável | Local |
|------------|--------|
| Três templates de prompt + chains LCEL + explicações didáticas | **[`exercicio_03_sem_ecra.ipynb`](exercicio_03_sem_ecra.ipynb)** (código **completo** no notebook, sem `from app.chains import …`) |
| Cópia modular (API / reutilização) | [`app/chains/eduprompt_chains.py`](app/chains/eduprompt_chains.py) — espelha a lógica do notebook |
| Documentação por chain | [`docs/chains.md`](docs/chains.md) |
| Docker | [`Dockerfile`](Dockerfile), [`docker-compose.yml`](docker-compose.yml) |

## Exemplo de entrada

```json
{
  "tema": "RAG",
  "nivel": "iniciante"
}
```

## Exemplo de saída (estrutura)

```markdown
## Explicação
RAG é uma técnica que combina busca em documentos com geração de texto.
…

## Exercícios
1. Explique o que é embedding.
2. Descreva a função de um retriever.
3. Monte um fluxo simples de RAG.

## Resumo
- …
```

(O texto exacto depende do modelo; o formato é montado por `gerar_pacote_educacional`.)

## Desafio extra

**Quarta chain:** narrativa sarcástica nerd — `chain_narrativa_nerd()` e rota `POST /eduprompt/narrativa-nerd`.

## Como executar

**Notebook (sem ecrã — predefinição):**

```bash
./run.sh
```

**API (opcional):**

```bash
./run_api.sh
```

- `GET http://localhost:8000/health`
- `POST http://localhost:8000/eduprompt/pacote` — corpo JSON `{ "tema": "RAG", "nivel": "iniciante" }`
- `POST http://localhost:8000/eduprompt/narrativa-nerd`

Variáveis: `GOOGLE_API_KEY` no `.env` na raiz do repositório do curso ([`.env.example`](.env.example)).

## Documentação adicional

- [`docs/arquitetura.md`](docs/arquitetura.md)
- [`docs/explicacao_teorica.md`](docs/explicacao_teorica.md)
- [`docs/passo_a_passo.md`](docs/passo_a_passo.md)
- [`docs/resultados.md`](docs/resultados.md)

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
