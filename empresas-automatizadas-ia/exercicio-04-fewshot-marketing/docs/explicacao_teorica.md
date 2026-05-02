# Teoria — Few-shot, Instructor e validação

## Few-shot vs zero-shot

- **Zero-shot:** só instruções gerais («escreve um post sobre X»).
- **Few-shot:** instruções **e** exemplos de entrada/saída desejados. O modelo alinha-se ao **padrão** observado nos exemplos (tom, comprimento, estrutura).

## Por que LangChain aqui?

`ChatPromptTemplate` separa **parte estável** (exemplos + regras de marca) da **parte variável** (produto, público, tom, preset de estilo), facilitando testes e evolução do copy deck.

## Instructor

Encapsula **tool calling / JSON schema** do provider e **reexecuta** quando a resposta não valida o modelo Pydantic (`max_retries`). Reduz código manual de parsing e de «conserta o JSON».

## Pydantic na campanha

Garante tipos, cardinalidade de hashtags e tamanhos mínimos — útil antes de gravar em CRM ou publicar.
