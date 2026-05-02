# Explicação teórica — Exercício 02: Atendimento 360

## Memória de conversa (foco pedagógico)

Ver o documento dedicado: **[`memoria_conversa.md`](memoria_conversa.md)** — sessão vs prompt, lista explícita, limpar memória e limites de contexto.

## Memória de sessão (implementação)

- **Streamlit:** `st.session_state["history"]` mantém a lista entre reruns.
- **Notebook:** a lista `h` (ou equivalente) é o mesmo padrão sem UI; exportação JSON reutiliza a mesma estrutura.

## Context window

Históricos longos enchem o contexto do modelo — **truncar**, **resumir** ou **arquivar** é necessário em produção. O exercício mantém o histórico completo para clareza; em cenários reais mede-se tokens e aplica-se política de janela.