# Passo a passo — RAG Jurídico

1. Na raiz do **repositório do curso**, configure `.env` com `GOOGLE_API_KEY`.
2. Opcional: `GEMINI_MODEL_EX06`, `GEMINI_EMBEDDING_MODEL_EX06` (ver `.env.example` nesta pasta).
3. Arranque a stack: `./run_api.sh` ou `./run_api.sh --fg`.
4. Indexação inicial **dentro do contentor**:  
   `docker compose exec app python scripts/indexar.py`
5. Teste CLI:  
   `docker compose exec app python scripts/consultar.py`  
   ou API `POST /perguntar` (ver `docs/API.md`).
6. Parar: `docker compose down`.
