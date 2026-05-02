# Arquitetura — Exercício 01: PromptLab Consultoria

## Visão técnica
Entrada validada (Pydantic) → seleção de perfil → `SystemMessage` fixo por perfil → `HumanMessage` com a pergunta → modelo Gemini → texto da resposta.

## Componentes
- **Interface sem ecrã:** notebook executável célula a célula.
- **Opcional:** API FastAPI em `app/` espelha o mesmo contrato JSON (`./run_api.sh`).

## Fluxo de dados
```text
JSON/células → Schema perfil+pergunta → Prompt sistema → LLM → AIMessage → texto
```

## Coordenações multi-agente (`/coordenacao`)

Além do endpoint único `/responder` (um perfil), existem **cinco modos** que combinam vários agentes:

| Modo | Coordenação |
|------|-------------|
| `sequencial_pipeline` | Saída técnica → reformulação didática → camada comercial |
| `paralelo_sintese` | Três perfis em **paralelo** (`ThreadPoolExecutor`) → agente **sintetizador** |
| `debate_critico` | Técnico → crítico sarcástico → técnico revisado |
| `router_inteligente` | Classificador estruturado (`with_structured_output`) → um perfil |
| `refinamento_triplo` | Professor → técnico corrige → comercial empacota |

Implementação: `app/chains/coordenacoes.py`, prompts auxiliares em `app/services/prompts_coordenacao.py`.

## Extensões
Rate limiting, cache por hash (perfil+pergunta), testes unitários com LLM mockado.
