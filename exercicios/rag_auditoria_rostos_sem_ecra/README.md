# RAG multimodal — relatórios de auditoria, rostos (LFW) e dados estruturados

Exercício **sem interface gráfica**: Jupyter via Docker, como nos outros módulos `*_sem_ecra`.

## O que faz

- Gera **relatórios Markdown** fictícios de auditoria, um **Parquet/CSV** de achados (`findings`) e exporta **imagens de rostos** a partir do conjunto **Labeled Faces in the Wild** (`fetch_lfw_people` do scikit-learn).
- Indexa texto com embeddings **Sentence-Transformers** (MiniLM) em **ChromaDB**.
- Indexa imagens com **CLIP** (embeddings visuais) numa segunda coleção Chroma.
- Demonstra **consulta unificada** (texto + imagem + filtro nos dados estruturados) e síntese opcional com **Gemini** (`GOOGLE_API_KEY` no `.env` na raiz do repositório).

## Como executar

Na raiz desta pasta:

```bash
./run.sh
```

Abra no browser o URL com token que o Jupyter imprimir. Notebook principal: `exercicio_rag_auditoria_sem_ecra.ipynb`.

Na primeira execução o download do LFW e dos pesos dos modelos pode demorar; a imagem Docker é pesada por causa do PyTorch.

**Build (Chroma em Apple Silicon / aarch64):** a imagem Jupyter usa `minimal-notebook:python-3.12.11` (não `latest`) para evitar falha ao compilar `chroma-hnswlib` com Python 3.13.

## Ética e dados

As fotos **LFW** são rostos públicos para investigação; no exercício são usadas apenas como **substituto técnico** de “amostras visuais”. Não use este fluxo para vigilância ou identificação de pessoas reais sem base legal e governança adequadas.

## Documentação extra

- `docs/arquitetura.md`, `docs/explicacao_teorica.md`, `docs/passo_a_passo.md`

## Export estático (`CODIGO_COMPLETO`)

Na **raiz do repositório**, `python exercicios/gerar_codigo_completo_txt.py` gera nesta pasta:

- **`CODIGO_COMPLETO.txt`** — leitura offline / impressão (formato com `#` nas células markdown).
- **`CODIGO_COMPLETO.md`** — o mesmo corpo dentro de um bloco `~~~text` para pré-visualização em Markdown.

## Regenerar o `.ipynb`

```bash
python3 create_notebook.py
```
