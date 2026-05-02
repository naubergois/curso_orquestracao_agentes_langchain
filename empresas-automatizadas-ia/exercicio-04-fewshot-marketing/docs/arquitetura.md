# Arquitetura — Exercício 04: FewShot Marketing

## Fluxo

```text
GerarCampanhaEntrada (produto, publico, tom, estilo)
       ↓
ChatPromptTemplate (LangChain) — system com few-shot + human com briefing
       ↓
messages → formato OpenAI-like {role, content}
       ↓
Instructor + Google Gemini — create(response_model=Campanha)
       ↓
Campanha validada (Pydantic)
```

## Ficheiros

| Componente | Ficheiro |
|------------|----------|
| Schema / presets | `app/schemas/campanha.py` |
| Prompt few-shot + Instructor | `app/services/gerador_campanha.py` |
| API | `app/main.py` |

## Docker

- **API:** `docker compose up` na pasta do exercício (porta 8000).
- **Jupyter:** `./run.sh` → `docker-compose.jupyter.yml`.
