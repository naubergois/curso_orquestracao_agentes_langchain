"""Interface Streamlit — laudos fictícios, Postgres, Chroma, LangGraph + agente chat."""

from __future__ import annotations

import json

import streamlit as st
from langchain_core.messages import HumanMessage

import agente_chat
import chroma_ingest
import db_laudos
import graph_avaliacao

st.set_page_config(page_title="Laudos clínicos (demo)", layout="wide", initial_sidebar_state="expanded")

st.title("Laudos laboratoriais — demo multi-agente")
st.caption(
    "Dados **fictícios**. PostgreSQL + ChromaDB + LangGraph (avaliação Pydantic) + agente ReAct para discussão clínica. "
    "Requer `GOOGLE_API_KEY` no `.env`."
)


def _suffix() -> int:
    return int(st.session_state.get("thread_suffix", 0))


def _hist_key(pid: int) -> str:
    return f"msgs_{pid}_{_suffix()}"


def _ensure_graph() -> None:
    if "react_graph" not in st.session_state:
        st.session_state.react_graph = agente_chat.criar_agente_chat_medico()


def _ensure_chroma(rebuild: bool) -> None:
    with st.spinner("A indexar / carregar Chroma (pode demorar na primeira vez)…"):
        vs = chroma_ingest.garantir_indice_chroma(reconstruir=rebuild)
        agente_chat.configurar_rag(vs.as_retriever(search_kwargs={"k": 6}))


_ensure_graph()

with st.sidebar:
    st.subheader("Índice semântico")
    if st.button("Reindexar Chroma (apagar coleção demo)"):
        _ensure_chroma(rebuild=True)
        st.success("Chroma reindexado.")
        st.rerun()
    if st.button("Garantir Chroma (sem apagar)"):
        _ensure_chroma(rebuild=False)
        st.success("Chroma pronto.")
        st.rerun()

    st.divider()
    st.subheader("Motor LangGraph")
    st.caption("Pipeline: carregar laudos → Gemini + Pydantic → gravar em `avaliacoes_engine`.")

try:
    pacientes = db_laudos.listar_pacientes_resumo()
except Exception as e:
    st.error(f"Erro ao ligar ao PostgreSQL: {e}")
    st.stop()

if not pacientes:
    st.warning("Sem pacientes na base — verifique o `init_db`.")
    st.stop()

if "chroma_inicializado" not in st.session_state:
    try:
        _ensure_chroma(rebuild=False)
        st.session_state.chroma_inicializado = True
    except Exception as e:
        st.error(f"Chroma / embeddings: {e}")
        st.info("Confirme `GOOGLE_API_KEY` e volte a tentar, ou use «Reindexar Chroma» na barra lateral.")
        st.stop()

opts = {f"{p['id']} — {p['nome_completo']} ({p['idade']}a)": int(p["id"]) for p in pacientes}
label = st.selectbox("Paciente activo", list(opts.keys()))
pid = opts[label]

col_a, col_b = st.columns([1, 2])

with col_a:
    st.subheader("Ficha")
    f = db_laudos.ficha_paciente(pid)
    if f:
        st.markdown(
            f"**{f['nome_completo']}**\n\n"
            f"- Idade: {f['idade']}\n"
            f"- Sexo: {f.get('sexo')}\n"
            f"- Alergias: {f.get('alergias')}\n"
            f"- Notas: {f.get('observacoes_clinicas')}"
        )
    st.subheader("Última gravidade (Postgres)")
    av = db_laudos.ultima_avaliacao_dict(pid)
    if av:
        st.metric("Score", int(av.get("score") or 0), help="0–100 no cenário-demo")
        st.write("**Nível:**", av.get("nivel_gravidade"))
        payload = av.get("payload_json")
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                pass
        if isinstance(payload, dict):
            st.markdown("**Riscos**")
            for r in payload.get("riscos_imediatos") or []:
                st.markdown(f"- {r}")
            st.markdown("**Hipóteses**")
            for h in payload.get("hipoteses_patologicas") or []:
                st.markdown(f"- {h}")
    else:
        st.info("Ainda sem avaliação — use o botão abaixo.")

    if st.button("Correr pipeline de avaliação (LangGraph)", type="primary"):
        with st.spinner("A avaliar…"):
            try:
                out = graph_avaliacao.executar_avaliacao(pid)
                if out.get("erro"):
                    st.error(out["erro"])
                else:
                    st.success("Avaliação gravada.")
            except Exception as e:
                st.exception(e)
        st.rerun()

    if st.button("Limpar conversa deste paciente (nova thread)"):
        st.session_state.thread_suffix = _suffix() + 1
        k = _hist_key(pid)
        if k in st.session_state:
            del st.session_state[k]
        st.rerun()

with col_b:
    st.subheader("Chat médico (ReAct + Postgres + RAG)")
    hk = _hist_key(pid)
    if hk not in st.session_state:
        st.session_state[hk] = []

    for role, text in st.session_state[hk]:
        with st.chat_message(role):
            st.markdown(text)

    if prompt := st.chat_input("Pergunte sobre hipóteses, riscos ou dados laboratoriais…"):
        st.session_state[hk].append(("user", prompt))
        cfg = agente_chat.config_chat(pid, thread_suffix=_suffix())
        try:
            out = st.session_state.react_graph.invoke({"messages": [HumanMessage(content=prompt)]}, cfg)
            resp = agente_chat.ultima_resposta_assistente(out)
        except Exception as e:
            resp = f"**Erro:** `{e}`"
        st.session_state[hk].append(("assistant", resp))
        st.rerun()
