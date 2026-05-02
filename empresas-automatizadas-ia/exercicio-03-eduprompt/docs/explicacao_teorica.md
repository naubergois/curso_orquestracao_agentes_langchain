# Explicação teórica — Exercício 03: EduPrompt Academy

## PromptTemplate vs ChatPromptTemplate

O enunciado fala em **PromptTemplate**. Para **modelos de chat** (Gemini, GPT, etc.), o ecossistema LangChain usa **`ChatPromptTemplate`**: define mensagens `system` / `human` / `ai` que o `ChatModel` consome.

- **`PromptTemplate`** (string única `{variáveis}`) é típico de LLMs tipo *completion*.
- **`ChatPromptTemplate`** é o equivalente **composable** quando cada turno tem papel explícito — mantém o mesmo espírito LCEL do enunciado.

Ambos ligam-se ao modelo com o operador **`|`** e ao **`StrOutputParser`** para obter texto simples.

## LCEL (LangChain Expression Language)

- **`|`** — `RunnableSequence`: saída de um passo entra no seguinte.
- **`RunnableParallel`** — várias chains partilham o **mesmo** dicionário de entrada (`tema`, `nivel`).
- **Reutilização** — prompts e parsers são objetos imutáveis; o modelo pode ser injetado nas factories para testes.

## StrOutputParser

Extrai o **conteúdo textual** da resposta do chat como `str`, evitando lidar manualmente com tipos de mensagem na UI ou no notebook.

## Leitura recomendada

- [`chains.md`](chains.md) — uma secção por chain.
