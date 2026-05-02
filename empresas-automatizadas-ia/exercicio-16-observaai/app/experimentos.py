"""Três prompts, métricas, MLflow e ficheiro local para o dashboard Streamlit."""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import mlflow
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

_EX_ROOT = Path(__file__).resolve().parents[1]
_ML = _EX_ROOT / "data" / "mlruns"
_JSONL = _EX_ROOT / "data" / "runs.jsonl"

PROMPTS = {
    "p1": "Responde em PT-PT com uma frase.",
    "p2": "Responde em PT-PT com passos numerados e conclusão.",
    "p3": "Responde em PT-PT como FAQ: pergunta reformulada, resposta, aviso de limitações.",
}


def _llm():
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").replace("models/", "")
    return ChatGoogleGenerativeAI(model=model, temperature=0.3)


def _estimar_custo_chars(n_chars: int) -> float:
    """Heurística ilustrativa (USD)."""
    return round((n_chars / 1000.0) * 0.0002, 6)


def correr_entrada(entrada: str, avaliacao_manual: str | None = None) -> dict:
    os.makedirs(_ML, exist_ok=True)
    mlflow.set_tracking_uri(f"file:{_ML}")
    mlflow.set_experiment("observaai_prompts")

    llm = _llm()
    linhas = []

    for pid, sys_prompt in PROMPTS.items():
        rid = str(uuid.uuid4())
        t0 = time.perf_counter()
        err = None
        out = ""
        try:
            msg = llm.invoke(
                [SystemMessage(content=sys_prompt), HumanMessage(content=entrada)]
            )
            out = getattr(msg, "content", str(msg)) or ""
        except Exception as e:
            err = str(e)
        ms = int((time.perf_counter() - t0) * 1000)
        custo = _estimar_custo_chars(len(entrada) + len(out or ""))
        registro = {
            "run_id": rid,
            "ts": datetime.now(timezone.utc).isoformat(),
            "prompt_id": pid,
            "entrada": entrada,
            "saida": out,
            "erro": err,
            "latencia_ms": ms,
            "custo_estimado_usd": custo,
            "avaliacao": avaliacao_manual,
        }
        linhas.append(registro)

        with mlflow.start_run(run_name=f"{pid}-{rid[:8]}"):
            mlflow.log_param("prompt_id", pid)
            mlflow.log_param("entrada_len", len(entrada))
            mlflow.log_metric("latencia_ms", ms)
            mlflow.log_metric("custo_estimado_usd", custo)
            mlflow.log_text(entrada, "entrada.txt")
            mlflow.log_text(out or "", "saida.txt")
            if err:
                mlflow.log_text(err, "erro.txt")
            if avaliacao_manual:
                mlflow.log_param("avaliacao_manual", avaliacao_manual)

    _JSONL.parent.mkdir(parents=True, exist_ok=True)
    with _JSONL.open("a", encoding="utf-8") as f:
        for r in linhas:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return {"resultados": linhas, "mlflow_uri": f"file:{_ML}", "jsonl": str(_JSONL)}
