"""Interface web que consome a API do projeto integrador."""

from __future__ import annotations

import os

import requests
import streamlit as st

API = os.environ.get("API_URL", "http://localhost:8020")

st.set_page_config(page_title="Empresa Autónoma Integrada", layout="wide")
st.title("Empresa Autónoma Integrada")
st.caption(f"API: `{API}`")

msg = st.text_area("Mensagem do utilizador", height=140)

if st.button("Executar pipeline"):
    if not msg.strip():
        st.error("Escreva uma mensagem.")
    else:
        try:
            r = requests.post(f"{API.rstrip('/')}/pipeline", json={"mensagem": msg.strip()}, timeout=120)
            r.raise_for_status()
            data = r.json()
            st.subheader("Classe")
            st.write(data.get("classe_demanda"))
            st.subheader("Resposta ao cliente (revisada)")
            st.write(data.get("resposta_cliente"))
            st.subheader("Relatório interno")
            st.write(data.get("relatorio_interno"))
            st.subheader("Avaliação automática (extra)")
            st.write(data.get("avaliacao_automatica"))
            with st.expander("Logs"):
                st.code("\n".join(data.get("logs") or []))
        except Exception as e:
            st.exception(e)
