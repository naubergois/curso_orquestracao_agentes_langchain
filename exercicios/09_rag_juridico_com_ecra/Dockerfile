# Streamlit — ex. 9 com ecrã. Contexto de build: pasta `exercicios/` (ver docker-compose.yml).
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
  && rm -rf /var/lib/apt/lists/*

COPY 09_rag_juridico_com_ecra/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY lib_llm_fallback.py .
COPY 09_rag_juridico_sem_ecra/agent_gerador_pdfs.py \
     09_rag_juridico_sem_ecra/gerar_pdfs_conceitos.py \
     09_rag_juridico_sem_ecra/ingest_rag.py \
     09_rag_juridico_sem_ecra/db_processos.py \
     09_rag_juridico_sem_ecra/rag_juridico.py \
     sem_ecra/
COPY 09_rag_juridico_com_ecra/streamlit_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
