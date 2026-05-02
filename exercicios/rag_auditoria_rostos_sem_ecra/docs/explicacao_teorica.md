# Teoria — RAG, semântica multimodal e dados estruturados

## RAG sobre relatórios

Fragmentação (*chunking*) dos Markdown aumenta a precisão da recuperação; embeddings densos capturam sinonímia (ex.: “incumprimento” vs “descumprimento”).

## Busca por palavra-chave vs semântica

- **Keyword**: rápida, falha com reformulações.
- **Semântica**: robusta a variação lexical; custo de índice e latência de embedding.

## CLIP e imagens de rostos

CLIP foi treinado com pares imagem–texto; o mesmo modelo projeta texto e imagem num espaço comparável. Permite perguntas como “rostos associados a alterações em payroll” — o modelo recupera imagens cujo contexto textual associado (nas fichas) foi semelhante, dentro dos limites da demo.

## Dados estruturados

`pandas` permite filtros exatos (valor > X, risco == alto) complementares à recuperação textual (“fuzziness”). O notebook junta os dois: **SQL-like mental** + **RAG**.

## Ética e LFW

O LFW contém figuras públicas; uso aqui é **estritamente educacional**. Os relatórios são **fictícios**; os códigos `PERS_XXX` anonimizam o papel no cenário de auditoria.
