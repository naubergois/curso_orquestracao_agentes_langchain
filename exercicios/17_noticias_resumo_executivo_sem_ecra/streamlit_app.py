"""Tela Streamlit — boletim do exercício 17 + agente de frontend do exercício 18 (Nielsen)."""

from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# Docker: `agente_frontend.py` na mesma pasta de trabalho. Local: pasta do ex. 18 no repo.
_APP = Path(__file__).resolve().parent
if not (_APP / "agente_frontend.py").is_file():
    _ex18 = _APP.parent / "18_agente_frontend_design"
    if _ex18.is_dir() and str(_ex18) not in sys.path:
        sys.path.insert(0, str(_ex18))

from agente_frontend import (
    build_graph as build_graph_design,
    obter_mensagens_do_thread,
    proxima_mensagem_utilizador,
    texto_para_mostrar,
)
from noticias_agentes import executar_pipeline_noticias


def _inject_theme_css() -> None:
    st.markdown(
        """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap');
  .stApp {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    background: linear-gradient(165deg, #eef2ff 0%, #f8fafc 40%, #f0fdf4 100%);
  }
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.25);
  }
  section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  section[data-testid="stSidebar"] .stMarkdown strong { color: #f8fafc !important; }
  .stButton > button[kind="primary"] {
    border-radius: 10px;
    font-weight: 600;
    background: linear-gradient(135deg, #059669, #2563eb);
    border: none;
  }
  .metric-card {
    background: #fff;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
  }
  h1 { letter-spacing: -0.02em; color: #0f172a !important; }
</style>
        """,
        unsafe_allow_html=True,
    )


def _ultimo_html_design(msgs: list) -> str | None:
    pat = re.compile(r"```\s*html\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
    for m in reversed(msgs):
        if not isinstance(m, AIMessage):
            continue
        c = m.content
        if not isinstance(c, str):
            continue
        match = pat.search(c)
        if match:
            return match.group(1).strip()
    return None


def _sidebar() -> None:
    st.markdown("### Exercício 17 + 18")
    st.markdown(
        "**17:** pipeline de notícias (DuckDuckGo + Pydantic + indicadores).\n\n"
        "**18:** agente ReAct com heurísticas **Nielsen** — use-o para HTML/CSS "
        "de um *dashboard* ou para refinar a apresentação dos dados."
    )
    st.divider()
    st.markdown("#### Nielsen (resumo)")
    st.caption(
        "Estado visível · Mundo real · Controlo · Consistência · Prevenir erros · "
        "Reconhecimento · Eficiência · Minimalismo · Erros recuperáveis · Ajuda"
    )
    if st.button("Limpar boletim da sessão", use_container_width=True):
        st.session_state.pop("boletim_payload", None)
        st.rerun()
    if st.button("Nova conversa com o agente 18", use_container_width=True):
        st.session_state.design_thread_id = str(uuid.uuid4())
        st.rerun()


st.set_page_config(
    page_title="Boletim + Agente UI",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)
_inject_theme_css()

if "design_thread_id" not in st.session_state:
    st.session_state.design_thread_id = str(uuid.uuid4())


@st.cache_resource
def graph_design():
    return build_graph_design()


g_design = graph_design()

st.title("Boletim de notícias")
st.markdown(
    "Gera o **boletim** (exercício 17) e, na aba seguinte, pede ao **agente de frontend** "
    "(exercício 18) layouts ou melhorias com base nas heurísticas de Nielsen."
)

_sidebar()

tab_boletim, tab_design = st.tabs(["Boletim (ex. 17)", "Agente de interface (ex. 18)"])

with tab_boletim:
    c1, c2 = st.columns([3, 1], gap="medium")
    with c1:
        consulta = st.text_input(
            "Consulta de pesquisa",
            value=st.session_state.get("consulta_default", "notícias de hoje Portugal economia política"),
            help="Será enviada ao agente de pesquisa do exercício 17 (várias chamadas DuckDuckGo).",
            key="inp_consulta",
        )
    with c2:
        st.write("")
        st.write("")
        gerar = st.button("Gerar boletim", type="primary", use_container_width=True)

    if gerar:
        with st.status("A correr o pipeline (pesquisa Web + estruturação + resumo)…", expanded=True) as stt:
            try:
                payload = executar_pipeline_noticias(
                    consulta.strip(),
                    thread_pesquisa=f"ui17-{uuid.uuid4().hex[:8]}",
                    thread_redator=f"ui17r-{uuid.uuid4().hex[:8]}",
                )
                st.session_state.boletim_payload = payload
                st.session_state.consulta_default = consulta.strip()
                stt.update(label="Boletim pronto", state="complete")
            except Exception as e:
                stt.update(label="Falhou", state="error")
                st.error(str(e))

    payload = st.session_state.get("boletim_payload")
    if not payload:
        st.info("Introduza uma consulta e carregue em **Gerar boletim** (Nielsen 1: estado visível durante o processamento).")
    else:
        ind = payload["indicadores"]
        bol = payload["boletim"]
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Notícias", ind.total_noticias)
        with m2:
            st.metric("Relevância média", f"{ind.relevancia_media:.1f}")
        with m3:
            st.metric("Categorias distintas", ind.diversidade_categorias)
        with m4:
            st.metric("Fracção internacional", f"{ind.fraccao_internacional:.0%}")

        if ind.contagem_por_categoria:
            df_cat = pd.DataFrame(
                [(k, v) for k, v in ind.contagem_por_categoria.items()],
                columns=["categoria", "quantidade"],
            )
            st.subheader("Distribuição por categoria")
            st.bar_chart(df_cat.set_index("categoria"))

        st.subheader("Resumo executivo (Markdown)")
        st.markdown(payload["resumo_executivo_markdown"])

        with st.expander("Resumo estruturado (Pydantic)", expanded=False):
            st.json(payload["resumo_executivo_estruturado"].model_dump())

        with st.expander("Boletim JSON", expanded=False):
            st.json(bol.model_dump())

        with st.expander("Relatório de pesquisa (bruto)", expanded=False):
            st.text_area("Fonte", payload["relatorio_pesquisa_bruto"], height=220, disabled=True)

with tab_design:
    st.subheader("Chat com o agente do exercício 18")
    st.caption(
        "Peça HTML/CSS responsivo para mostrar métricas e lista de notícias, "
        "ou refinamentos de acessibilidade. Use blocos ```html para pré-visualizar."
    )

    if st.session_state.get("boletim_payload"):
        if st.button("Atalho: HTML de dashboard para o último boletim", use_container_width=True):
            p = st.session_state.boletim_payload
            ctx = (
                "Com base nestes dados JSON do boletim (ex. 17), gera **um único** ficheiro HTML "
                "com CSS embutido em `<style>`: cards para métricas, lista de notícias com links, "
                "tipografia legível, contraste AA, foco visível e layout responsivo (Nielsen 4, 8). "
                "Responde com o bloco ```html … ```.\n\n"
                + p["boletim"].model_dump_json(indent=2)
            )
            with st.spinner("Agente a trabalhar…"):
                try:
                    proxima_mensagem_utilizador(g_design, ctx, st.session_state.design_thread_id)
                except Exception as e:
                    st.error(str(e))
            st.rerun()
    else:
        st.info("Gere primeiro um boletim na aba **Boletim** para usar o atalho com contexto.")

    msgs = obter_mensagens_do_thread(g_design, st.session_state.design_thread_id)
    for m in msgs:
        if isinstance(m, HumanMessage):
            with st.chat_message("user"):
                st.markdown(texto_para_mostrar(m) or "")
        elif isinstance(m, AIMessage):
            t = texto_para_mostrar(m)
            if t:
                with st.chat_message("assistant"):
                    st.markdown(t)
        elif isinstance(m, ToolMessage):
            with st.chat_message("assistant"):
                st.markdown(texto_para_mostrar(m) or "")

    prompt = st.chat_input("Mensagem para o agente de frontend…")
    if prompt:
        with st.spinner("A processar…"):
            try:
                proxima_mensagem_utilizador(g_design, prompt, st.session_state.design_thread_id)
            except Exception as e:
                st.error(str(e))
        st.rerun()

    snippet = _ultimo_html_design(obter_mensagens_do_thread(g_design, st.session_state.design_thread_id))
    if snippet:
        st.subheader("Pré-visualização HTML (agente 18)")
        safe = snippet[:120_000]
        if re.search(r"<\s*html[\s>]", safe, re.I) or re.match(r"\s*<!doctype", safe, re.I):
            doc = safe
        else:
            doc = (
                "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                "</head><body style='margin:0;padding:12px;font-family:system-ui,sans-serif'>"
                f"{safe}</body></html>"
            )
        components.html(doc, height=480, scrolling=True)
