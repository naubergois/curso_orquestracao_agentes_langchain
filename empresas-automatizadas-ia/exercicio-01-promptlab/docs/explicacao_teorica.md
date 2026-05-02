# Explicação teórica — Exercício 01: PromptLab Consultoria

## System prompt vs user prompt
O *system* define papel, tom e limites; o *user* traz a pergunta concreta. Variar só o system mantém comparável o comportamento do modelo entre perfis.

## Pydantic na entrada
Enums impedem valores de perfil inválidos; `Field` documenta limites e ajuda OpenAPI quando há API.

## AIMessage
É o envelope LangChain para saída do modelo; extrai-se `content` para texto simples.

## Coordenação entre agentes
“Agente” aqui é um **mesmo modelo** com **system prompts** diferentes (papéis). Os padrões implementados são:

- **Pipeline sequencial** — cada etapa consome a saída da anterior (compressão de informação e mudança de tom).
- **Paralelo + síntese** — baixa correlação entre erros se os três raciocínios são independentes; o sintetizador resolve conflitos explicitamente.
- **Debate** — introduz *segunda opinião* antes da versão final (útil para reduzir complacência).
- **Router** — reduz custo/latência escolhendo **um** papel em vez de orquestrar todos.
- **Refinamento triplo** — ordem pedagógica ↔ rigor ↔ empacotamento comercial.

Trade-offs: mais etapas ⇒ mais chamadas ao modelo, maior custo e tempo; paralelo reduz *wall-clock* antes da síntese.