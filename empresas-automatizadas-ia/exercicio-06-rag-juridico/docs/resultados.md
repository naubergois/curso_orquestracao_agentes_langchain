# Resultados esperados — RAG Jurídico (Ex. 6)

## Funcional

- `python scripts/indexar.py` conclui sem erro e cria `data/chroma_juridico/`.
- `python scripts/consultar.py` (ou `POST /perguntar`) devolve `resposta` e lista **`fontes`** com `arquivo`, `score` e `trecho`.
- Perguntas sobre **prazo de resposta contratual** recuperam trechos das normas/contrato fictícios (15 dias úteis).

## Qualidade

- Resposta em **português europeu**, fundamentada nos trechos quando o retriever acerta.
- Erro claro se o índice ainda não foi criado.

## Avaliação

- Explicar o fluxo: Loader → índice → Chroma → query engine.
- Discutir limitações: custo API, quota, qualidade do chunking, necessidade de atualizar o índice quando os `.md` mudam.
