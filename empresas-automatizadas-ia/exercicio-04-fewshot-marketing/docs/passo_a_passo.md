# Passo a passo — Exercício 04

1. Configurar `GOOGLE_API_KEY` no `.env` na raiz do repositório do curso.
2. **Jupyter:** na pasta do exercício, `./run.sh` → abrir `exercicio_04_sem_ecra.ipynb`.
3. **API:** `./run_api.sh` → `POST http://localhost:8000/campanhas/gerar` com JSON de briefing.
4. Experimentar `GET /campanhas/estilos` e alterar o campo `estilo` no POST.
5. Parar: `docker compose -f docker-compose.jupyter.yml down` ou `docker compose down`.
