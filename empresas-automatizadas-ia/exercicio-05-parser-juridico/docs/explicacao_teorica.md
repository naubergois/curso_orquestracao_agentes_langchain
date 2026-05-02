# Explicação teórica — Exercício 5: Parser Jurídico

## Extração de informação estruturada

Objetivo: mapear **texto livre** para um **contrato de dados** fixo (campos tipados). Isto permite integrações (CRM, fluxos de aprovação, dashboards) sem parsing frágil por expressões regulares.

## Validação da saída

- **Pydantic v2** garante tipos, comprimentos e literais (`risco`, `prioridade`).
- **Instructor** reexecuta / corrige quando o modelo falha o schema (dentro de `max_retries`).

## Guardrails vs Instructor

O enunciado pede **Guardrails AI** *ou* **Instructor**. Neste projeto usa-se **Instructor** com **Gemini** por consistência com o resto do curso. *Guardrails* poderia acrescentar políticas declarativas (PII, tom, tópicos proibidos) — o **screening jurídico** (`ScreeningJuridico`) cumpre o papel mínimo de **bloqueio** quando o input não é jurídico.

## Tratamento de erros

- **422** — corpo inválido (texto curto) ou **texto não jurídico** após screening.
- **503** — chave API em falta ou falha ao contactar o modelo (quota, rede).

## Limitações pedagógicas

A API **não** substitui parecer jurídico; o `resumo` deve permanecer factual. Em produção acrescentar-se-iam logs, tracing, limites de taxa e revisão humana.
