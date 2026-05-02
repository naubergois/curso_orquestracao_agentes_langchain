# Arquitetura — Exercício 09: HelpDesk Agent

## Visão técnica
Agente ReAct simplificado: modelo escolhe entre ferramentas Python (`@tool`) que simulam ticketing.

## Fluxo
```text
mensagem → agent → tool calls → observações → resposta final
```
