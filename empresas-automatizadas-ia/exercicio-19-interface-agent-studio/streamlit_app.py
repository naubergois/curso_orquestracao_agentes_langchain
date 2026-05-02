"""Interface Streamlit — Exercício 19."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
# Raiz do repositório do curso (dois níveis acima desta pasta de exercício)
load_dotenv(_ROOT.parent.parent / ".env", override=False)
load_dotenv(_ROOT / ".env", override=True)

from app.agent_shared import responder  # noqa: E402

st.set_page_config(page_title="Agent Studio — Streamlit", layout="centered")
st.title("Interface Agent Studio (Streamlit)")

if not os.environ.get("GOOGLE_API_KEY"):
    st.warning("Defina GOOGLE_API_KEY para usar o agente.")

modelo = st.selectbox("Modelo", ["gemini-2.0-flash", "gemini-1.5-flash"])
tom = st.selectbox("Tom", ["profissional", "didático", "informal"])
temp = st.slider("Temperatura", 0.0, 1.0, 0.3, 0.05)
msg = st.text_area("Mensagem", height=160)

if st.button("Enviar"):
    if not msg.strip():
        st.error("Escreva uma mensagem.")
    else:
        with st.spinner("A gerar..."):
            try:
                out = responder(msg.strip(), modelo, temp, tom)
                st.success(out)
            except Exception as e:
                st.exception(e)
