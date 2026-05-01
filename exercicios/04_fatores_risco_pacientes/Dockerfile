# Contexto de build: pasta `exercicios/` (ver docker-compose.yml).
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY 04_fatores_risco_pacientes/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY lib_llm_fallback.py .
COPY 04_fatores_risco_pacientes/agent.py .
COPY 04_fatores_risco_pacientes/streamlit_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
