# Exercício 20 — mercantil, relatórios em paralelo (LangChain + Pydantic) + agente

Simula **compras** (entrada de mercadoria) e **vendas**; gera **relatório de stock** e **relatório de lucro e vendas** ao mesmo tempo com **`RunnableParallel`** (LCEL). Os relatórios são instâncias **Pydantic v2** (`RelatorioEstoque`, `RelatorioLucroVendas`). Um **agente ReAct** (LangGraph + Gemini), em `mercantil_agente_analise.py`, usa *tools* que devolvem esses JSON para produzir **análise** integrada.

**Arranque:** `./run.sh` nesta pasta. **`GOOGLE_API_KEY`** para o agente e para a secção opcional do caderno; **`GEMINI_MODEL_EX20`** opcional.
