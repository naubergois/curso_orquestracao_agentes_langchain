# Exercício 18 — agente LangChain para desenvolvimento de frontend

Agente **ReAct** (LangGraph + Gemini) orientado pelas **10 heurísticas de Nielsen** e pelo **guia de design moderno e responsivo**.

## Integração com o exercício 17

- **Ferramenta** `executar_boletim_noticias_ex17`: corre o pipeline de notícias (DuckDuckGo, Pydantic, indicadores, resumo) para o agente de UI consumir dados reais.
- **Streamlit** (duas abas): **Boletim (ex. 17)** chama `executar_pipeline_noticias` directamente; **Agente (ex. 18)** mantém o chat, atalhos (incluindo «Boletim + dashboard HTML»), pré-visualização HTML e botão para enviar o JSON do boletim já gerado como contexto.

O *build* Docker usa a **raiz do repositório** como contexto e copia `noticias_agentes.py` do ex. 17 para o contentor.

## Executar

```bash
cd exercicios/18_agente_frontend_design
./run.sh
```

Abrir `http://localhost:8501` (ou `STREAMLIT_PORT`). **Internet** necessária para notícias.

## Variáveis

- `GOOGLE_API_KEY` (`.env` na raiz)
- Opcional: `GEMINI_MODEL_EX18` (agente Nielsen), `GEMINI_MODEL_EX17` (pipeline de notícias), `GEMINI_MODEL`
