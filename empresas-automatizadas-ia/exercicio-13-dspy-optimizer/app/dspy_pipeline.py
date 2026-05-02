"""Pipeline DSPy: duas variantes de prompt e métrica composta (extra)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import dspy


def _lm():
    model = os.environ.get("GEMINI_MODEL_DSPY", os.environ.get("GEMINI_MODEL", "gemini/gemini-2.0-flash"))
    if not model.startswith("gemini/") and "/" not in model:
        model = f"gemini/{model.replace('models/', '')}"
    return dspy.LM(model, api_key=os.environ["GOOGLE_API_KEY"])


class RespostaCurta(dspy.Signature):
    """Responde em PT-PT numa única frase curta."""

    pergunta: str = dspy.InputField()
    resposta: str = dspy.OutputField()


class RespostaDetalhada(dspy.Signature):
    """Responde em PT-PT com contexto breve, passos numerados quando fizer sentido e conclusão."""

    pergunta: str = dspy.InputField()
    resposta: str = dspy.OutputField()


def claridade_completude_precisao(pred: str, gold_hint: str) -> dict:
    """Métrica simples 0–1 em três eixos (desafio extra)."""
    t = (pred or "").strip().lower()
    palavras = re.findall(r"\w+", t)
    completude = min(1.0, len(palavras) / 25.0)
    markers = sum(1 for k in ["1.", "2.", "passo", "primeiro", "segundo"] if k in t)
    claridade = min(1.0, 0.35 + 0.2 * markers)
    hint = (gold_hint or "").lower()
    precisao = 1.0 if hint and any(w in t for w in hint.split()) else max(0.2, min(0.6, completude))
    total = round((claridade + completude + precisao) / 3, 3)
    return {"claridade": round(claridade, 3), "completude": round(completude, 3), "precisao": round(precisao, 3), "total": total}


def carregar_dataset() -> list[dict]:
    path = Path(__file__).resolve().parents[1] / "data" / "perguntas.json"
    return json.loads(path.read_text(encoding="utf-8"))


def avaliar() -> dict:
    dspy.configure(lm=_lm())
    mod_curto = dspy.ChainOfThought(RespostaCurta)
    mod_longo = dspy.ChainOfThought(RespostaDetalhada)
    rows = []
    curto_tot = longo_tot = 0.0
    for item in carregar_dataset():
        q = item["pergunta"]
        gold = item.get("resposta_esperada", "")
        r1 = mod_curto(pergunta=q)
        r2 = mod_longo(pergunta=q)
        m1 = claridade_completude_precisao(getattr(r1, "resposta", str(r1)), gold)
        m2 = claridade_completude_precisao(getattr(r2, "resposta", str(r2)), gold)
        curto_tot += m1["total"]
        longo_tot += m2["total"]
        rows.append(
            {
                "id": item["id"],
                "pergunta": q,
                "curta": {"texto": getattr(r1, "resposta", str(r1)), "metrica": m1},
                "detalhada": {"texto": getattr(r2, "resposta", str(r2)), "metrica": m2},
            }
        )
    n = max(len(rows), 1)
    return {
        "media_curta": round(curto_tot / n, 4),
        "media_detalhada": round(longo_tot / n, 4),
        "linhas": rows,
        "nota": "A variante detalhada tende a pontuar melhor na métrica de claridade/completude.",
    }
