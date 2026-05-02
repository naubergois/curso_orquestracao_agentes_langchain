"""Dashboard simples (desafio extra) lendo data/runs.jsonl."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

_ROOT = Path(__file__).resolve().parent
_PATH = _ROOT / "data" / "runs.jsonl"


def _carregar() -> pd.DataFrame:
    if not _PATH.exists():
        return pd.DataFrame()
    rows = []
    with _PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return pd.DataFrame(rows)


st.set_page_config(page_title="ObservaAI", layout="wide")
st.title("ObservaAI — últimas execuções")
st.caption("Depois de `POST /experimentos`, os registos aparecem aqui.")

df = _carregar()
if df.empty:
    st.info("Ainda sem dados. Chame a API `POST /experimentos` com uma entrada.")
else:
    df = df.sort_values("ts", ascending=False) if "ts" in df.columns else df
    cols = [c for c in ["ts", "prompt_id", "latencia_ms", "custo_estimado_usd", "erro", "avaliacao"] if c in df.columns]
    st.dataframe(df[cols], use_container_width=True)
    if "run_id" not in df.columns:
        st.stop()
    rid = st.selectbox("Run", df["run_id"].tolist())
    row = df.loc[df["run_id"] == rid].iloc[0]
    st.subheader("Entrada")
    st.write(row.get("entrada", ""))
    st.subheader("Saída")
    st.write(row.get("saida", ""))
