"""Interface Streamlit — notícias (ex. 17) + agente de frontend Nielsen (ex. 18)."""

from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

_APP = Path(__file__).resolve().parent
if not (_APP / "noticias_agentes.py").is_file():
    _ex17 = _APP.parent / "17_noticias_resumo_executivo_sem_ecra"
    if _ex17.is_dir() and str(_ex17) not in sys.path:
        sys.path.insert(0, str(_ex17))

from noticias_agentes import executar_pipeline_noticias  # type: ignore[import-untyped]

from agente_frontend import (
    build_graph,
    obter_mensagens_do_thread,
    proxima_mensagem_utilizador,
    texto_para_mostrar,
)

_PRESETS = [
    (
        "Boletim + dashboard HTML",
        "Chama `executar_boletim_noticias_ex17` com a consulta «notícias Portugal economia hoje» e, com o JSON, gera um único ficheiro HTML+CSS responsivo (cards de métricas + lista de notícias), bloco ```html … ```.",
    ),
    ("Formulário de contacto acessível", "Gera HTML+CSS de um formulário de contacto responsivo com validação visual e mensagens de erro claras (Nielsen 5, 9)."),
    ("Dashboard cards (genérico)", "Layout responsivo em CSS Grid com cards de métricas; foco visível e hierarquia clara (Nielsen 4, 8)."),
    ("Navegação móvel", "Menu de navegação mobile-first com botão hamburger, aria-expanded e fecho ao clicar fora (Nielsen 7, 10)."),
]


def _inject_theme_css() -> None:
    st.markdown(
        """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,600;0,700;1,400&display=swap');
  .stApp {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    background: linear-gradient(165deg, #eef2ff 0%, #f8fafc 35%, #ecfeff 100%);
  }
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.25);
  }
  section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
  }
  section[data-testid="stSidebar"] .stMarkdown a {
    color: #7dd3fc !important;
  }
  div[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
  }
  div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
  }
  .stButton > button[kind="primary"] {
    border-radius: 10px;
    font-weight: 600;
    padding: 0.5rem 1rem;
    background: linear-gradient(135deg, #2563eb, #4f46e5);
    border: none;
  }
  .stTextInput > div > div > input, .stChatInput textarea {
    border-radius: 10px !important;
    border: 1px solid #cbd5e1 !important;
  }
  h1 { letter-spacing: -0.02em; color: #0f172a !important; }
  .hero-caption { color: #475569; font-size: 1.05rem; max-width: 52rem; }
</style>
        """,
        unsafe_allow_html=True,
    )


def _ultimo_html_resposta(msgs: list) -> str | None:
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


def _sidebar_nielsen() -> None:
    st.markdown("### Ex. 17 + 18")
    st.caption(
        "**17:** pipeline de notícias (DuckDuckGo, Pydantic, indicadores). "
        "**18:** agente ReAct Nielsen — inclui a *tool* `executar_boletim_noticias_ex17` para dados reais."
    )
    st.divider()
    st.markdown("### Heurísticas de Nielsen")
    st.caption("O agente pode abrir a lista completa via ferramenta.")
    pairs = [
        ("1", "Estado visível"),
        ("2", "Mundo real"),
        ("3", "Controlo"),
        ("4", "Consistência"),
        ("5", "Prevenir erros"),
        ("6", "Reconhecimento"),
        ("7", "Eficiência"),
        ("8", "Minimalismo"),
        ("9", "Recuperar erros"),
        ("10", "Ajuda"),
    ]
    for num, title in pairs:
        with st.expander(f"{num}. {title}"):
            st.markdown("Use **`referencia_heuristicas_nielsen`** no chat para o texto integral.")
    st.divider()
    st.markdown("### Acessibilidade")
    st.markdown(
        "- Contraste AA\n- Foco visível\n- `prefers-reduced-motion`\n- Alvos ≥ 44px"
    )


st.set_page_config(
    page_title="Notícias + Frontend Nielsen",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)
_inject_theme_css()

st.title("Notícias e agente de frontend")
st.markdown(
    '<p class="hero-caption"><strong>Ex. 17</strong> — boletim e indicadores. '
    "<strong>Ex. 18</strong> — agente ReAct com Nielsen e *tool* que corre o mesmo pipeline de notícias para alimentar UI/HTML.</p>",
    unsafe_allow_html=True,
)

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


@st.cache_resource
def graph():
    return build_graph()


g = graph()

with st.sidebar:
    _sidebar_nielsen()
    st.divider()
    st.markdown("### Atalhos (ex. 18)")
    for label, prompt in _PRESETS:
        key = "p_" + str(abs(hash(label)))
        if st.button(label, key=key, use_container_width=True):
            st.session_state["_preset_send"] = prompt
    st.divider()
    if st.button("Nova conversa (agente 18)", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.pop("_preset_send", None)
        st.rerun()
    if st.button("Limpar boletim (ex. 17)", use_container_width=True):
        st.session_state.pop("boletim_payload", None)
        st.rerun()
    st.caption("Streamlit **8501** por defeito. Requer rede para notícias.")

preset = st.session_state.pop("_preset_send", None)
if preset:
    with st.spinner("A enviar atalho ao agente…"):
        try:
            proxima_mensagem_utilizador(g, preset, st.session_state.thread_id)
        except Exception as e:
            st.error(str(e))
    st.rerun()

tab_news, tab_design = st.tabs(["Boletim de notícias (ex. 17)", "Agente de interface (ex. 18)"])

with tab_news:
    st.subheader("Pipeline de notícias")
    c1, c2 = st.columns([3, 1])
    with c1:
        q = st.text_input(
            "Consulta",
            value=st.session_state.get("consulta_ui", "notícias de hoje Portugal economia política"),
            key="news_q",
        )
    with c2:
        st.write("")
        st.write("")
        go = st.button("Gerar boletim", type="primary", use_container_width=True)

    if go:
        with st.status("A correr agentes de pesquisa e estruturação (ex. 17)…", expanded=True) as stt:
            try:
                st.session_state.boletim_payload = executar_pipeline_noticias(
                    q.strip(),
                    thread_pesquisa=f"ui18n-{uuid.uuid4().hex[:8]}",
                    thread_redator=f"ui18nr-{uuid.uuid4().hex[:8]}",
                )
                st.session_state.consulta_ui = q.strip()
                stt.update(label="Concluído", state="complete")
            except Exception as e:
                stt.update(label="Erro", state="error")
                st.error(str(e))

    pl = st.session_state.get("boletim_payload")
    if not pl:
        st.info("Gere um boletim ou use a aba **Agente** com o atalho «Boletim + dashboard HTML».")
    else:
        ind = pl["indicadores"]
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Notícias", ind.total_noticias)
        with m2:
            st.metric("Relevância média", f"{ind.relevancia_media:.1f}")
        with m3:
            st.metric("Categorias", ind.diversidade_categorias)
        with m4:
            st.metric("Internacional", f"{ind.fraccao_internacional:.0%}")
        if ind.contagem_por_categoria:
            df = pd.DataFrame(
                [(k, v) for k, v in ind.contagem_por_categoria.items()],
                columns=["categoria", "n"],
            )
            st.bar_chart(df.set_index("categoria"))
        st.markdown("#### Resumo executivo")
        st.markdown(pl["resumo_executivo_markdown"])
        with st.expander("JSON do boletim"):
            st.json(pl["boletim"].model_dump())

with tab_design:
    col_chat, col_preview = st.columns((1.15, 1.0), gap="large")
    with col_chat:
        st.subheader("Conversa com o agente (ex. 18)")
        if st.session_state.get("boletim_payload"):
            if st.button("Enviar resumo do boletim ao agente como contexto", use_container_width=True):
                p = st.session_state.boletim_payload
                ctx = (
                    "Contexto do boletim já gerado na outra aba (JSON):\n```json\n"
                    + p["boletim"].model_dump_json(indent=2)[:12000]
                    + "\n```\nSugere melhorias de UI ou HTML para o apresentar (Nielsen)."
                )
                with st.spinner("A processar…"):
                    try:
                        proxima_mensagem_utilizador(g, ctx, st.session_state.thread_id)
                    except Exception as e:
                        st.error(str(e))
                st.rerun()

        msgs = obter_mensagens_do_thread(g, st.session_state.thread_id)
        for m in msgs:
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
                    st.markdown(texto_para_mostrar(m) or "")

        user_text = st.chat_input("Pedido de UI / HTML / integração com notícias…")
        if user_text:
            with st.status("Agente a trabalhar (pode invocar notícias ou Nielsen)…", expanded=True) as status:
                try:
                    proxima_mensagem_utilizador(g, user_text, st.session_state.thread_id)
                    status.update(label="Concluído", state="complete")
                except Exception as e:
                    status.update(label="Erro", state="error")
                    st.error(f"**Erro:** {e}")
            st.rerun()

    with col_preview:
        st.subheader("Pré-visualização HTML")
        st.caption("Último bloco ` ```html ` da conversa do agente 18.")
        msgs2 = obter_mensagens_do_thread(g, st.session_state.thread_id)
        snippet = _ultimo_html_resposta(msgs2)
        if snippet:
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
            components.html(doc, height=520, scrolling=True)
        else:
            st.info("Peça HTML em markdown ou use o atalho «Boletim + dashboard HTML».")

with st.expander("Ajuda (Nielsen 10)", expanded=False):
    st.markdown(
        """
- Na aba **Boletim**, obtém dados reais (rede + Gemini).
- Na aba **Agente**, o modelo pode chamar **`executar_boletim_noticias_ex17`** sozinho ou receber o JSON que já geraste.
- Peça sempre **```html** para pré-visualizar.
        """
    )
