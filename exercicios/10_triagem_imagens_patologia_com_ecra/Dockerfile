# Streamlit — ex. 10 com ecrã. Contexto de build: pasta `exercicios/`.
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
  && rm -rf /var/lib/apt/lists/*

COPY 10_triagem_imagens_patologia_com_ecra/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY lib_llm_fallback.py .
COPY 10_triagem_imagens_patologia_sem_ecra/agent_triagem.py \
     10_triagem_imagens_patologia_sem_ecra/classificador.py \
     10_triagem_imagens_patologia_sem_ecra/cnn_derma.py \
     10_triagem_imagens_patologia_sem_ecra/mongo_store.py \
     10_triagem_imagens_patologia_sem_ecra/triagem.py \
     10_triagem_imagens_patologia_sem_ecra/treinar_classificador.py \
     sem_ecra/
COPY 10_triagem_imagens_patologia_com_ecra/streamlit_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
