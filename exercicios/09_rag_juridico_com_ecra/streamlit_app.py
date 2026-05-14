"""RAG sobre PDFs jurídicos (ex. 9) — várias coleções Chroma (embeddings distintos)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
# `lib_llm_fallback.py` e outros utilitários partilhados vivem em `exercicios/`.
sys.path.insert(0, str(HERE.parent))
for _extra in (HERE / "sem_ecra", HERE.parent / "09_rag_juridico_sem_ecra"):
    if _extra.is_dir():
        sys.path.insert(0, str(_extra))

for d in (HERE, HERE.parent, *HERE.parents):
    env = d / ".env"
    if env.is_file():
        load_dotenv(env, override=False)
        break

# Antes de `import ingest_rag` / Chroma (telemetria PostHog vs. chromadb).
os.environ.setdefault("ANONYMIZED_TELEMETRY", "false")
os.environ.setdefault("CHROMADB_ANONYMIZED_TELEMETRY", "false")

st.set_page_config(page_title="Ex. 09 — RAG jurídico", page_icon="⚖️")

st.title("Exercício 09 — RAG com Chroma e vários embeddings")
st.caption(
    "PDFs em `pdf_fontes/` podem ser **estáticos** (ReportLab) ou gerados por **agente** (Gemini + tool). "
    "O Chroma usa três coleções: **FastEmbed** local (MiniLM multilingual ONNX), **gemini-embedding-001** e "
    "**gemini-embedding-2-preview** (espaços de vetores distintos). "
    "**PostgreSQL** guarda **processos fictícios** ligados aos PDFs (RAG híbrido: dados estruturados + excertos). "
    "Pedagógico; não é aconselhamento jurídico."
)


def _base_sem_ecra() -> Path:
    for p in (HERE / "sem_ecra", HERE.parent / "09_rag_juridico_sem_ecra"):
        if (p / "ingest_rag.py").is_file():
            return p.resolve()
    return (HERE / "sem_ecra").resolve()


def _persist_chroma() -> Path:
    return _base_sem_ecra() / "chroma_juridico"


@st.cache_resource
def _llm_chat():
    from lib_llm_fallback import gemini_model_candidates, make_gemini_chat_with_runtime_fallback

    prim = (
        os.environ.get("GEMINI_MODEL_EX09")
        or os.environ.get("GEMINI_MODEL")
        or "gemini-2.0-flash"
    ).strip()
    candidatos = gemini_model_candidates(primary=prim)
    return make_gemini_chat_with_runtime_fallback(candidatos, temperature=0.2)


@st.cache_resource
def _retriever(collection_name: str, persist_dir_str: str):
    from ingest_rag import carregar_vectorstore

    vs = carregar_vectorstore(collection_name, Path(persist_dir_str))
    return vs.as_retriever(search_kwargs={"k": 5})


with st.sidebar:
    st.subheader("Índice")
    fonte = st.radio(
        "Origem dos PDFs",
        ("estatico", "agente"),
        format_func=lambda x: "Texto fixo no código" if x == "estatico" else "Agente ReAct (Gemini + rede)",
        help="«Agente» chama o LLM várias vezes via LangGraph; requer quota de API.",
    )
    if st.button("Regenerar PDFs e reindexar Chroma", type="primary"):
        from ingest_rag import pipeline_completo

        with st.spinner(
            "Pipeline completo (FastEmbed pode demorar na primeira vez; agente precisa de rede)…"
        ):
            pipeline_completo(
                persist_directory=_persist_chroma(),
                limpar_chroma=True,
                fonte_pdfs=fonte,
            )
        st.success("Concluído. A actualizar a página…")
        st.cache_resource.clear()
        st.rerun()

    from ingest_rag import listar_factories_embeddings

    opcoes = list(listar_factories_embeddings().keys())
    coleccao = st.selectbox("Coleção / embedding", opcoes, index=0)
    rag_modo = st.radio(
        "Modo RAG",
        ("pdf", "hibrido"),
        format_func=lambda x: "Só PDFs (Chroma)" if x == "pdf" else "Híbrido: PDFs + processos (PostgreSQL)",
        help="O modo híbrido exige o serviço `db` no `docker compose` e `DATABASE_URL` apontando para o Postgres.",
    )

if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
    st.warning(
        "Sem `GOOGLE_API_KEY` / `GEMINI_API_KEY`, a coleção **FastEmbed** (local) pode indexar‑se; "
        "o **chat**, o **agente** que gera PDFs e as coleções **Gemini** precisam da chave."
    )

persist = _persist_chroma()
chroma_pronto = persist.is_dir() and any(persist.iterdir())
if not chroma_pronto:
    st.warning(
        f"Ainda não há índice Chroma em `{persist}`. "
        "Use **Regenerar PDFs e reindexar Chroma** na barra lateral (a primeira ingestão pode demorar). "
        "Depois pode fazer perguntas RAG abaixo."
    )

if chroma_pronto:
    pergunta_teste = st.text_input("Pergunta de teste ao índice (só excertos)", "O que é um negócio jurídico?")
    if pergunta_teste:
        try:
            from ingest_rag import carregar_vectorstore

            _vs = carregar_vectorstore(coleccao, persist)
            docs = _vs.similarity_search(pergunta_teste, k=4)
            with st.expander("Documentos mais semelhantes (top‑k)"):
                for i, d in enumerate(docs, 1):
                    st.markdown(f"**{i}.** `{d.metadata.get('source', '?')}`")
                    st.text(d.page_content[:800] + ("…" if len(d.page_content) > 800 else ""))
        except Exception as e:
            st.error(f"Erro ao consultar a coleção `{coleccao}`: {e}")

if "msgs" not in st.session_state:
    st.session_state.msgs = []

for role, text in st.session_state.msgs:
    with st.chat_message(role):
        st.markdown(text)

if not chroma_pronto:
    st.caption("O chat fica desactivado até existir índice Chroma — use **Regenerar PDFs e reindexar Chroma** na barra lateral.")

user = st.chat_input(
    "Pergunta ao assistente (RAG + Gemini)…",
    disabled=not chroma_pronto,
)
if user and chroma_pronto:
    with st.chat_message("user"):
        st.markdown(user)
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        msg = "Defina a chave API no `.env` para usar o chat com Gemini."
        with st.chat_message("assistant"):
            st.markdown(msg)
        st.session_state.msgs.append(("user", user))
        st.session_state.msgs.append(("assistant", msg))
    else:
        try:
            from rag_juridico import construir_cadeia_rag, construir_cadeia_rag_hibrido

            ret = _retriever(coleccao, str(persist))
            if rag_modo == "hibrido":
                try:
                    from db_processos import contexto_sql_para_rag

                    _probe = contexto_sql_para_rag("processo", limite=1)
                except Exception as db_e:
                    st.warning(
                        "PostgreSQL indisponível ou vazio — a usar **só PDFs**. "
                        f"Detalhe: {db_e}"
                    )
                    chain = construir_cadeia_rag(_llm_chat(), ret)
                else:
                    chain = construir_cadeia_rag_hibrido(_llm_chat(), ret)
            else:
                chain = construir_cadeia_rag(_llm_chat(), ret)
            with st.chat_message("assistant"):
                with st.spinner("A gerar…"):
                    resp = chain.invoke({"pergunta": user})
                st.markdown(resp)
            st.session_state.msgs.append(("user", user))
            st.session_state.msgs.append(("assistant", resp))
        except Exception as e:
            with st.chat_message("assistant"):
                st.error(str(e))
            st.session_state.msgs.append(("user", user))
            st.session_state.msgs.append(("assistant", f"Erro: {e}"))

if st.sidebar.button("Limpar histórico do chat"):
    st.session_state.msgs = []
    st.rerun()
