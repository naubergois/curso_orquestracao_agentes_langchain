# Arquitetura — RAG Jurídico (Ex. 6)

## Visão

Serviço que combina **LlamaIndex** com **ChromaDB** para RAG sobre ficheiros Markdown em `data/juridico/`. A síntese da resposta usa **Gemini**; os vectores usam **Gemini Embeddings** (nomes configuráveis por variável de ambiente).

## Componentes

| Peça | Função |
|------|--------|
| `scripts/indexar.py` | Invoca `indexar_documentos()` — recria a coleção Chroma e ingere documentos |
| `scripts/consultar.py` | Invoca `consultar_com_fontes()` — impressão legível ou `--json` |
| `app/rag/pipeline.py` | Cliente Chroma persistente, `VectorStoreIndex`, query engine |
| `app/main.py` | `POST /perguntar` expõe o mesmo pipeline em JSON |

## Persistência

- **Origem:** apenas `.md` em `data/juridico/`.
- **Destino:** `data/chroma_juridico/` (`.gitignore`; gerado após indexação).

## Telemetria Chroma

`chromadb.PersistentClient(..., settings=Settings(anonymized_telemetry=False))` para reduzir ruído em ambientes com dependências de telemetria desalinhadas.
