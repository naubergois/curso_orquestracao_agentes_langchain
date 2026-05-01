"""Interface Streamlit — apenas apresentação e estado da sessão."""

import streamlit as st
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from agent import append_user_message, run_agent_turn


def message_to_display(msg: BaseMessage) -> str | None:
    if isinstance(msg, HumanMessage):
        return msg.content if isinstance(msg.content, str) else str(msg.content)
    if isinstance(msg, AIMessage):
        if getattr(msg, "tool_calls", None):
            return None
        return msg.content if isinstance(msg.content, str) else str(msg.content)
    return None


def render_chat(messages: list[BaseMessage]) -> None:
    for m in messages:
        if isinstance(m, HumanMessage):
            with st.chat_message("user"):
                st.markdown(message_to_display(m) or "")
        elif isinstance(m, AIMessage) and not getattr(m, "tool_calls", None):
            with st.chat_message("assistant"):
                st.markdown(message_to_display(m) or "")
        elif isinstance(m, ToolMessage):
            with st.chat_message("assistant"):
                st.caption(f"🔧 Ferramenta → {m.content}")


st.set_page_config(page_title="Agente Gemini (LangChain)", page_icon="🤖")

st.title("Alô mundo — agente LangChain + Gemini")
st.caption("O agente pode responder e usar a ferramenta de cumprimento quando fizer sentido.")

if "agent_messages" not in st.session_state:
    st.session_state.agent_messages: list[BaseMessage] = []

render_chat(st.session_state.agent_messages)

user_text = st.chat_input("Digite sua mensagem…")

if user_text:
    st.session_state.agent_messages = append_user_message(st.session_state.agent_messages, user_text)

    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            new_messages, reply = run_agent_turn(st.session_state.agent_messages)
            st.session_state.agent_messages = new_messages
        except Exception as e:
            reply = f"**Erro:** {e}"
        placeholder.markdown(reply)
