# Arquitetura — Exercício 02: Atendimento 360

## Visão técnica
Estado conversacional como lista ordenada de mensagens `{role, content}` reconstruída em mensagens LangChain antes de cada invocação.

## Por que lista em vez de memória automática?
Control explícito do que entra no contexto, exportação trivial (.json/.txt) e equivalência pedagógica ao `st.session_state`.

## Fluxo
```text
histórico → + user → SystemMessage + Human/AI alternados → Gemini → nova AIMessage → append histórico
```

## Streamlit (entrega com ecrã)

```text
Utilizador → Streamlit Chat → st.session_state["history"]
          → conversão LangChain (System + Human/AI) → Gemini → resposta → append histórico
```

`app/main.py` + `./run_streamlit.sh` na porta **8501**. O notebook `exercicio_02_sem_ecra.ipynb` é a versão auditável **sem ecrã**, com geração de conversas em lote e extração Pydantic.
