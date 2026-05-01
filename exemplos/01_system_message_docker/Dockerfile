FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Argumentos extra (mensagem humana) passam-se com: docker compose run --rm app "a tua pergunta"
ENTRYPOINT ["python", "-u", "main.py"]
CMD []
