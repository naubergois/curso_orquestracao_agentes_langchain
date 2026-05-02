# Documentação das chains — EduPrompt Academy

**Nota:** a versão **didática completa** (com explicações passo a passo) está no notebook [`exercicio_03_sem_ecra.ipynb`](../exercicio_03_sem_ecra.ipynb). Este ficheiro resume cada chain para consulta rápida.

Cada pipeline segue o padrão do enunciado:

```text
(tema, nivel) → PromptTemplate (ChatPromptTemplate) → ChatModel → StrOutputParser → texto
```

Implementação: [`app/chains/eduprompt_chains.py`](../app/chains/eduprompt_chains.py).

Variáveis comuns nos templates: **`tema`**, **`nivel`** (ex.: `iniciante`, `intermediario`, `avancado`).

---

## 1. Chain «Gerador de explicação»

- **Objetivo:** produzir uma explicação didática em 2–4 parágrafos, adequada ao nível.
- **Template:** `PROMPT_EXPLICACAO` — mensagem `system` (persona EduPrompt) + `human` com instruções de estrutura.
- **Saída:** texto corrido (sem `##`; o notebook ou API acrescentam o cabeçalho «## Explicação»).
- **Função:** `chain_explicacao()` → `Runnable` (`invoke({"tema": "...", "nivel": "..."})`).

---

## 2. Chain «Gerador de exercícios»

- **Objetivo:** três tarefas numeradas (`1.` … `3.`) alinhadas ao tema e ao nível.
- **Template:** `PROMPT_EXERCICIOS`.
- **Saída:** lista numerada em texto.
- **Função:** `chain_exercicios()`.

---

## 3. Chain «Gerador de resumo»

- **Objetivo:** síntese em 4–6 bullets (`- `).
- **Template:** `PROMPT_RESUMO`.
- **Saída:** bullet points.
- **Função:** `chain_resumo()`.

---

## 4. Composição LCEL

- **Paralelo:** `parallel_educacional()` usa `RunnableParallel` para correr as três chains com um único `invoke` (menos latência perceived quando o backend paraleliza chamadas internas).
- **Pacote Markdown:** `gerar_pacote_educacional()` devolve `explicacao`, `exercicios`, `resumo` e `markdown` já com `## Explicação`, `## Exercícios`, `## Resumo`.

---

## 5. Desafio extra — narrativa sarcástica nerd

- **Template:** `PROMPT_NARRATIVA_NERD` — tom ironico leve, uma equipa Produto vs Engenharia.
- **Função:** `chain_narrativa_nerd()`.
- **Nota:** uso humorístico; não substitui conteúdo pedagógico principal.

---

## StrOutputParser

Converte a mensagem do modelo numa **`str`** simples, facilitando concatenar Markdown e gravar ficheiros.
