# Memória de conversa — conceitos e prática (Atendimento 360)

## O problema que resolvemos

Numa central de suporte, o cliente **reclama**, **explica**, **muda de ideia**, **volta atrás** e espera que o sistema **lembre o que já foi dito**. Sem memória, cada mensagem parece isolada e o assistente contradiz-se ou repete perguntas — o equivalente a uma «reunião de segunda-feira» em que ninguém traz contexto.

## O que é «memória» aqui

Neste exercício, **memória** não é um modelo psicológico: é **estado conversacional** guardado entre turnos.

- **Histórico de mensagens:** lista ordenada de pares utilizador / assistente (e opcionalmente sistema).
- **Contexto acumulado:** tudo o que entra nessa lista é reenviado (ou processado) antes da próxima resposta do modelo.
- **Estado da sessão (Streamlit):** em `app/main.py`, o histórico vive em `st.session_state` para sobreviver a reruns do servidor da UI.

## Duas camadas importantes

1. **Memória na aplicação (UI / notebook)**  
   Onde guardamos as mensagens — por exemplo `st.session_state["history"]` ou uma lista `h` no Jupyter.

2. **Prompt com memória (LangChain)**  
   Antes de chamar o LLM, convertemos o histórico em `SystemMessage`, `HumanMessage`, `AIMessage`. O modelo só «lembra» o que **enviamos neste prompt** (sujeito ao limite de contexto).

## Por que usar lista explícita em vez de «memory» mágica

- **Transparência:** vês exatamente o que vai para o modelo.
- **Exportação:** `.txt` e `.json` são triviais.
- **Truncagem futura:** em produção, podes limitar tokens, resumir trechos antigos ou arquivar.

## Context window

Modelos têm limite de tokens. Históricos muito longos:

- enchem o contexto e ficam caros;
- podem empurrar instruções úteis para fora da «zona quente».

Soluções típicas: **resumo incremental**, **janela deslizante**, **memória externa** (vector store) — fora do âmbito mínimo deste exercício, mas mencionado nos extras do README.

## Limpar memória

«Limpar conversa» não apaga dados no servidor do modelo (stateless API): **reinicia a lista local**. O próximo prompt já não contém mensagens antigas.

## Leituras no repositório

- [`README.md`](../README.md) — onde o estado é guardado na app Streamlit.
- [`arquitetura.md`](arquitetura.md) — fluxo técnico resumido.
