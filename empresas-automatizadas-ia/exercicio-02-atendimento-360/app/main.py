"""Atendimento 360 — chat Streamlit com histórico na sessão e LangChain (Gemini)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


SYSTEM_PROMPT = (
    "És um assistente da empresa Atendimento 360. "
    "Respondes em português europeu, com cordialidade e mensagens claras e concisas. "
    "Usa o histórico desta conversa para responder de forma contextualizada."
)


def _llm() -> ChatGoogleGenerativeAI:
    model = (os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").strip().removeprefix("models/")
    return ChatGoogleGenerativeAI(model=model, temperature=0.35)


def _historico_para_mensagens(hist: list[dict[str, str]]) -> list[BaseMessage]:
    msgs: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
    for turno in hist:
        role = turno.get("role", "")
        content = turno.get("content", "")
        if role == "user":
            msgs.append(HumanMessage(content=content))
        elif role == "assistant":
            msgs.append(AIMessage(content=content))
    return msgs


def main() -> None:
    _carregar_env()
    st.set_page_config(page_title="Atendimento 360", page_icon="💬")
    st.title("Atendimento 360")
    st.caption("Histórico na sessão Streamlit · LangChain · Gemini")

    with st.sidebar:
        st.subheader("Exercício 2 — empresa simulada")
        st.markdown(
            "A **Atendimento 360** automatiza centrais de suporte com **histórico de conversa**."
        )
        st.markdown(
            "**Problema:** o cliente reclama, explica, muda de ideia e volta ao assunto anterior — "
            "espera que o sistema **lembre tudo** (uma espécie de reunião de segunda-feira)."
        )
        st.markdown(
            "**Estado:** lista em `st.session_state['history']` — ver secção no README."
        )

    if "history" not in st.session_state:
        st.session_state.history = []
    if not isinstance(st.session_state.history, list):
        st.session_state.history = []

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Limpar conversa"):
            st.session_state.history = []
            st.rerun()
    hist: list[dict[str, str]] = st.session_state.history
    texto_txt = "\n\n".join(
        f"{'Usuário' if m['role'] == 'user' else 'Assistente'}: {m['content']}" for m in hist
    )
    with c2:
        st.download_button(
            label="Exportar .txt",
            data=texto_txt or "(vazio)",
            file_name="historico_atendimento360.txt",
            mime="text/plain",
        )
    with c3:
        st.download_button(
            label="Exportar .json",
            data=json.dumps(hist, ensure_ascii=False, indent=2),
            file_name="historico_atendimento360.json",
            mime="application/json",
        )

    for m in hist:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Escreva a sua mensagem…"):
        hist.append({"role": "user", "content": prompt})
        st.session_state.history = hist

        with st.chat_message("user"):
            st.markdown(prompt)

        lc_msgs = _historico_para_mensagens(hist)
        try:
            ai: AIMessage = _llm().invoke(lc_msgs)
            reply = ai.content if isinstance(ai.content, str) else str(ai.content)
        except Exception as exc:
            reply = f"**Erro ao gerar resposta.** Verifique `GOOGLE_API_KEY` e quota. Detalhe: {exc}"

        hist.append({"role": "assistant", "content": reply})
        st.session_state.history = hist
        st.rerun()


if __name__ == "__main__":
    main()
