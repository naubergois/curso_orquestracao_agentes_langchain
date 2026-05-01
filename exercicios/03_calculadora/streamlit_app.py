"""Chat com agente ReAct + calculadora."""

import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agent import (
    build_graph,
    obter_mensagens_do_thread,
    proxima_mensagem_utilizador,
    texto_para_mostrar,
)

st.set_page_config(page_title="Ex. 03 — Calculadora", page_icon="🔢")

st.title("Exercício 03 — Agente com calculadora")
st.caption(
    "LangGraph `create_react_agent` com a tool **`calculadora`**. "
    "Ex.: «Qual é (20 + 15) * 3?» ou «Calcula 2**10». Porta Docker: **8501**."
)

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


@st.cache_resource
def graph():
    return build_graph()


g = graph()
for m in obter_mensagens_do_thread(g, st.session_state.thread_id):
    if isinstance(m, HumanMessage):
        with st.chat_message("user"):
            st.markdown(texto_para_mostrar(m) or "")
    elif isinstance(m, AIMessage):
        texto = texto_para_mostrar(m)
        if texto:
            with st.chat_message("assistant"):
                st.markdown(texto)
    elif isinstance(m, ToolMessage):
        with st.chat_message("assistant"):
            st.caption(texto_para_mostrar(m) or "")

user_text = st.chat_input("Escreve uma pergunta ou conta…")
if user_text:
    with st.spinner("O agente está a trabalhar…"):
        bar = st.progress(0, text="Gemini + ferramentas…")
        try:
            proxima_mensagem_utilizador(g, user_text, st.session_state.thread_id)
        except Exception as e:
            with st.chat_message("assistant"):
                st.error(f"**Erro:** {e}")
        finally:
            bar.empty()
    st.rerun()

with st.sidebar:
    if st.button("Nova conversa"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
