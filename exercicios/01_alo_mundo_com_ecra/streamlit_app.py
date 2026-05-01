"""Interface Streamlit — só desenha o chat e chama o `agent.py`."""

import streamlit as st

from agent import append_user_turn, build_chat_model, run_chat_turn


def render_chat(turnos: list[dict[str, str]]) -> None:
    for t in turnos:
        role, content = t["role"], t["content"]
        with st.chat_message(role):
            st.markdown(content)


st.set_page_config(page_title="Ex. 01 — LangChain + Gemini", page_icon="👋")

st.title("Exercício 01 — Alô mundo (com ecrã)")
st.caption(
    "O `agent.py` chama `.invoke()` com o **histórico completo** a cada mensagem — conversas muito "
    "longas enviam mais tokens e demoram mais. O cliente Gemini é reutilizado na sessão (evita recriar "
    "ligações HTTP). **Sem ecrã:** `01_alo_mundo_sem_ecra`."
)

if "historico" not in st.session_state:
    st.session_state.historico: list[dict[str, str]] = []
if "gemini_chat" not in st.session_state:
    st.session_state.gemini_chat = build_chat_model()

render_chat(st.session_state.historico)

user_text = st.chat_input("Escreve uma mensagem…")

if user_text:
    st.session_state.historico = append_user_turn(st.session_state.historico, user_text)
    with st.spinner("A processar o pedido ao Gemini…"):
        progress = st.progress(0, text="A aguardar resposta do Gemini…")
        try:
            st.session_state.historico, _ = run_chat_turn(
                st.session_state.historico,
                model=st.session_state.gemini_chat,
            )
        except Exception as e:
            st.session_state.historico = [
                *st.session_state.historico,
                {"role": "assistant", "content": f"**Erro:** {e}"},
            ]
        finally:
            progress.empty()
    st.rerun()
