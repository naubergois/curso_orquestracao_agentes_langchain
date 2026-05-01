"""Streamlit mínimo: só o último par pergunta/resposta (o modelo não guarda histórico)."""

import streamlit as st

from agent import responder

st.set_page_config(page_title="Ex. 02 — Nerd", page_icon="🤓")

st.title("Exercício 02 — Nerd sarcástico (com ecrã)")
st.caption(
    "Cada envio é **independente**: `SystemMessage` + a tua frase. Modelo por defeito **gemini-2.0-flash**; "
    "`GEMINI_MODEL_EX02` no `.env` para mudar. **Sem ecrã** (Jupyter): `02_nerd_sarcastico_sem_ecra`. "
    "**Docker:** `./run.sh` nesta pasta; porta **8501** por defeito."
)

if "ultima_pergunta" not in st.session_state:
    st.session_state.ultima_pergunta = None
if "ultima_resposta" not in st.session_state:
    st.session_state.ultima_resposta = None

if st.session_state.ultima_pergunta is not None:
    with st.chat_message("user"):
        st.markdown(st.session_state.ultima_pergunta)
    with st.chat_message("assistant"):
        st.markdown(st.session_state.ultima_resposta or "")

user_text = st.chat_input("Escreve algo…")

if user_text:
    st.session_state.ultima_pergunta = user_text
    with st.spinner("A pedir ao Gemini…"):
        progress = st.progress(0, text="À espera…")
        try:
            st.session_state.ultima_resposta = responder(user_text)
        except Exception as e:
            st.session_state.ultima_resposta = f"**Erro:** {e}"
        finally:
            progress.empty()
    st.rerun()
