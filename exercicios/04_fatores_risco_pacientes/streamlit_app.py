"""Chat com agente + PostgreSQL (pacientes fictícios), com progresso e análise por paciente."""

import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agent import (
    build_graph,
    mensagem_analise_um_paciente,
    obter_ids_nomes_pacientes,
    obter_mensagens_do_thread,
    proxima_mensagem_utilizador,
    texto_para_mostrar,
)

st.set_page_config(page_title="Ex. 04 — Fatores de risco", page_icon="🩺")

st.title("Exercício 04 — Pacientes e fatores de risco")
st.caption(
    "LangChain `create_agent` + **DeepSeek** (`ChatOpenAI`) + PostgreSQL. **Recomendado:** sidebar "
    "«Um paciente de cada vez». Variáveis: `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL` (predef.: deepseek-chat). "
    "Porta **8501**; Postgres no host **5433**."
)

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "pending_chat" not in st.session_state:
    st.session_state.pending_chat = ""


@st.cache_resource
def graph():
    return build_graph()


def _executar_mensagem(g, mensagem: str, thread_id: str) -> None:
    steps: list[int] = [0]

    def _passo_grafo() -> None:
        steps[0] += 1
        # Sem total fixo: aproximação até 95 % para não ficar preso antes do fim.
        pr.progress(min(0.14 * steps[0], 0.95), text=f"Modelo / ferramentas — passo {steps[0]}…")

    with st.status("O agente está a trabalhar…", expanded=True) as status_box:
        pr = st.progress(0.0, text="A iniciar…")
        try:
            proxima_mensagem_utilizador(
                g, mensagem, thread_id, on_stream_step=_passo_grafo
            )
            pr.progress(1.0, text="Concluído.")
            status_box.update(label="Concluído", state="complete")
        except Exception:
            status_box.update(label="Falhou", state="error")
            pr.empty()
            raise


g = graph()

if st.session_state.pending_chat:
    pend = st.session_state.pending_chat
    st.session_state.pending_chat = ""
    try:
        _executar_mensagem(g, pend, st.session_state.thread_id)
    except Exception as e:
        with st.chat_message("assistant"):
            st.error(f"**Erro:** {e}")
    st.rerun()

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

user_text = st.chat_input("Pergunta livre (evite «analisa todos» de uma vez — usa a sidebar)…")
if user_text:
    try:
        _executar_mensagem(g, user_text, st.session_state.thread_id)
    except Exception as e:
        with st.chat_message("assistant"):
            st.error(f"**Erro:** {e}")
    st.rerun()

with st.sidebar:
    st.markdown("### Um paciente de cada vez")
    st.caption("Menos passos LLM + tool do que listar e analisar no mesmo pedido.")
    pares = obter_ids_nomes_pacientes()
    if pares:
        etiquetas = [f"{pid} — {nome}" for pid, nome in pares]
        escolha = st.selectbox("Paciente", range(len(etiquetas)), format_func=lambda i: etiquetas[i])
        if st.button("Analisar fatores de risco", type="primary"):
            pid = pares[escolha][0]
            st.session_state.pending_chat = mensagem_analise_um_paciente(pid)
            st.rerun()
    else:
        st.warning("Sem ligação à base (ver `DATABASE_URL` / Postgres).")

    st.divider()
    if st.button("Nova conversa"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
