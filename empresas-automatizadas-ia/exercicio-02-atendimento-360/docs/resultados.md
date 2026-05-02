# Resultados esperados — Exercício 02: Atendimento 360

## Funcional

- Com `.env` válido, o notebook executa sem erros até ao relatório agregado.
- No exemplo *João*, o assistente usa o histórico para responder ao nome (depende do modelo, mas o contexto é enviado corretamente).
- Em `app/data/generated/relatorios/` aparecem JSON por conversa mais `RELATORIO_LOTE.md` / `.json`.
- Após a secção de analytics: `extracoes_consolidado.csv` (e `.parquet`), gráficos PNG de consolidação e projeção, e `projecao_volume_urgencia.csv`.

## Streamlit

- Mensagens aparecem em bolhas de chat; **Limpar conversa** esvazia o histórico.
- Downloads `.txt` e `.json` refletem o estado atual da sessão.

## Qualidade pedagógica

- Consegue explicar a diferença entre **estado na app** (`session_state`) e **contexto no prompt** (mensagens LangChain).
- Identifica limitações: quota API, custo por chamada na extração em lote, ausência de persistência entre sessões.

## Evolução

Truncagem de histórico por tokens, armazenamento em Redis/DB, avaliação humana sobre as extrações Pydantic.
