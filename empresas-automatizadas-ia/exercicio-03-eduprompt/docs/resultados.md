# Resultados esperados — Exercício 03: EduPrompt Academy

## Funcional

- Notebook executa sem erros com API key válida.
- Três chains devolvem texto em português europeu, alinhado ao nível pedido.
- `gerar_pacote_educacional` devolve `markdown` com três secções `##`.
- Chain extra devolve um parágrafo sarcástico sem conteúdo ofensivo.

## API

- `GET /health` retorna `status: ok`.
- `POST /eduprompt/pacote` devolve JSON com `explicacao`, `exercicios`, `resumo`, `markdown`.

## Avaliação

- Consegue descrever o papel de cada template e do `StrOutputParser`.
- Explica diferença entre sequência (`|`) e `RunnableParallel`.
