# Exercício 22 — **notícias do dia** (Web) + **FAISS** + **RAG** com dois agentes

1. **Agente de recolha** (`agente_recolha_noticias.py`): ReAct com *tools* **DuckDuckGo** e gravação do último resultado em **FAISS** (embeddings **Gemini** `gemini-embedding-001`).
2. **Agente analista** (`agente_analista_noticias_rag.py`): ReAct com uma *tool* que faz **similarity search** sobre o índice e redige **análises** só com base nos trechos recuperados.

**Requisitos:** `.env` na raiz do repositório com **`GOOGLE_API_KEY`** ou **`GEMINI_API_KEY`**. **Rede** para a pesquisa Web. Opcional: **`GEMINI_MODEL_EX22`**, **`GEMINI_EMBEDDING_MODEL`** (por defeito **`gemini-embedding-001`**; valores antigos como `text-embedding-004` são mapeados automaticamente).

**Arranque:** `./run.sh` nesta pasta (Jupyter sem token).

## Google Colab

1. Fazer *upload* do ficheiro **`exercicio_22_colab.ipynb`** para [Google Colab](https://colab.research.google.com/) (ou abrir a partir do GitHub se o repo estiver público).
2. **Runtime → Executar tudo**. Na primeira célula instala-se as dependências (`ddgs`, `faiss-cpu`, LangChain, etc.).
3. **Secrets:** no Colab, **ícone da chave → Adicionar secret** com o nome **`GOOGLE_API_KEY`** e o valor da [Google AI Studio](https://aistudio.google.com/apikey). Quando o Colab perguntar, permitir acesso ao secret a partir deste *notebook*.
4. Se não usar Secrets, a célula da chave pede a entrada com `getpass`.

Para **regenerar** o caderno Colab depois de editar os `.py`:

```bash
python3 gerar_exercicio_22_colab_ipynb.py
```

**Nota pedagógica:** o DuckDuckGo devolve *snippets*; em produção usar-se-ia uma API de notícias (NewsAPI, Tavily, etc.). O índice grava **apenas a última** pesquisa intermédia — para fundir vários ângulos, peça ao agente uma **consulta final abrangente** antes de gravar.
