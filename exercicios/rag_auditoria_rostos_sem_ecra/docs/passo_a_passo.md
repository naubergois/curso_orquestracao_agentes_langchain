# Passo a passo

1. Na raiz do repositório: `.env` com `GOOGLE_API_KEY`.
2. Nesta pasta: `chmod +x run.sh run_jupyter.sh` (uma vez).
3. `./run.sh` — primeira vez faz **build** grande (PyTorch + sentence-transformers).
4. Abrir `exercicio_rag_auditoria_sem_ecra.ipynb` e executar por ordem.
5. A primeira execução descarrega **LFW** via scikit-learn (requer rede no contentor).

Parar: `docker compose -f docker-compose.jupyter.yml down`.
