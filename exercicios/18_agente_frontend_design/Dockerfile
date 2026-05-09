# Build a partir da raiz do repo — inclui `noticias_agentes.py` do ex. 17.
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY exercicios/18_agente_frontend_design/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r /tmp/requirements.txt

COPY exercicios/18_agente_frontend_design/agente_frontend.py /app/
COPY exercicios/18_agente_frontend_design/streamlit_app.py /app/
COPY exercicios/17_noticias_resumo_executivo_sem_ecra/noticias_agentes.py /app/

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
