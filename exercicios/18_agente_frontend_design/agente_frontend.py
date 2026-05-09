"""Exercício 18 — agente LangChain (ReAct + Gemini) para desenvolvimento de frontend com heurísticas de Nielsen."""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

_NIELSEN_PT = """
1. Visibilidade do estado do sistema — feedback imediato (loading, sucesso, erros).
2. Correspondência entre o sistema e o mundo real — linguagem do utilizador, ícones familiares.
3. Controlo e liberdade do utilizador — desfazer, cancelar, voltar atrás.
4. Consistência e padrões — mesmos controlos e vocabulário em todo o lado.
5. Prevenção de erros — desactivar acções perigosas, confirmações claras.
6. Reconhecimento em vez de recordação — menus visíveis, ajuda contextual.
7. Flexibilidade e eficiência de uso — atalhos para experientes, defaults sensatos.
8. Estética e design minimalista — só o necessário, hierarquia visual clara.
9. Ajudar os utilizadores a reconhecer, diagnosticar e recuperar de erros — mensagens humanas, sugerir correção.
10. Ajuda e documentação — curta, pesquisável, passos concretos.
"""


@tool
def referencia_heuristicas_nielsen() -> str:
    """Devolve as 10 heurísticas de Nielsen (Jakob Nielsen) em português para guiar UI/UX."""
    return _NIELSEN_PT.strip()


@tool
def guia_design_moderno_responsivo() -> str:
    """Checklist compacta: HTML semântico, CSS responsivo, acessibilidade e performance."""
    return """
- HTML: header/nav/main/footer, landmarks ARIA quando útil, labels ligados a inputs (for/id).
- CSS: mobile-first; unidades fluidas (clamp, rem); grid/flex; max-width legível (~65ch texto).
- Toque: alvos ≥ 44×44px; espaçamento generoso entre acções.
- Contraste: preferir WCAG AA (4.5:1 texto normal); estados :hover/:focus-visible/:active visíveis.
- prefers-reduced-motion: respeitar animações curtas ou desactivar movimento.
- Tipografia: escala modular; line-height 1.45–1.6 em corpo; evitar texto só em maiúsculas longas.
- Formulários: erros inline junto ao campo; não só cor para estado (ícone/texto).
- Performance: imagens com loading lazy, formatos modernos; CSS crítico enxuto.
""".strip()


@tool
def executar_boletim_noticias_ex17(consulta: str) -> str:
    """Corre o **pipeline do exercício 17**: pesquisa Web (DuckDuckGo), boletim Pydantic, indicadores e resumo executivo.

    Usa quando precisares de **dados de notícias reais** para desenhar dashboards, landings ou componentes.
    Devolve JSON com `consulta`, `indicadores`, `itens` (notícias estruturadas), `resumo_executivo` e trecho de `resumo_markdown`.
    Argumento: consulta curta em português (ex.: «notícias economia Portugal hoje»).
    """
    from noticias_agentes import executar_pipeline_noticias

    u = uuid.uuid4().hex[:12]
    r = executar_pipeline_noticias(
        (consulta or "").strip(),
        thread_pesquisa=f"ex18-tool-p-{u}",
        thread_redator=f"ex18-tool-r-{u}",
    )
    bol = r["boletim"]
    ind = r["indicadores"]
    re = r["resumo_executivo_estruturado"]
    payload = {
        "consulta": r["consulta"],
        "indicadores": ind.model_dump(),
        "itens": [it.model_dump() for it in bol.itens],
        "resumo_executivo": re.model_dump(),
        "resumo_markdown": (r["resumo_executivo_markdown"] or "")[:4500],
    }
    return json.dumps(payload, ensure_ascii=False)


_SYSTEM = f"""És um **designer de produto e engenheiro de frontend** sénior. Ajudas a planear e a escrever código de interface (HTML/CSS/JS ou React/TSX) com **excelente usabilidade**.

Integração com **notícias (exercício 17)**:
- Quando o utilizador pedir *dashboard*, *boletim*, *notícias do dia* ou UI baseada em conteúdo actual, chama **`executar_boletim_noticias_ex17`** com uma consulta curta; usa o JSON devolvido para gerar HTML/CSS coerente (Nielsen 1: estado visível durante loading no cliente — explica spinners no teu código).

Obrigatório em cada resposta relevante para UI:
- Aplicar as **10 heurísticas de Nielsen** (usa a tool `referencia_heuristicas_nielsen` quando precisares de citar a lista completa).
- Seguir o **guia de design moderno e responsivo** (`guia_design_moderno_responsivo`) para detalhes técnicos.
- Entregar código **acessível**, **responsivo** e **legível**; comentários curtos só onde esclarecem decisão de UX.
- Preferir **progressive enhancement**; evitar dependências pesadas sem necessidade.
- Quando gerares HTML completo, fechar tags, incluir meta viewport em exemplos de página, e estados de foco visíveis.

Formato sugerido nas respostas:
1. **Decisões de UX** (2–5 bullets ligados a Nielsen).
2. **Código** em blocos markdown com linguagem correcta (`html`, `css`, `tsx`, etc.).
3. **Testes rápidos** que o utilizador pode fazer (teclado, zoom 200%, telemóvel).

Heurísticas (resumo interno):
{_NIELSEN_PT}
"""


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_local_env()

_DEFAULT_GEMINI = "gemini-2.0-flash"


def _ensure_api_key() -> None:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "Defina GOOGLE_API_KEY ou GEMINI_API_KEY no `.env` na raiz do repositório."
        )
    os.environ.setdefault("GOOGLE_API_KEY", key)


def _modelo() -> str:
    nome = (
        os.environ.get("GEMINI_MODEL_EX18") or os.environ.get("GEMINI_MODEL") or _DEFAULT_GEMINI
    ).strip() or _DEFAULT_GEMINI
    base = nome.removeprefix("models/")
    if base.startswith("gemini-1.5"):
        print(
            "Aviso: `gemini-1.5*` → `gemini-2.0-flash`. Ajuste GEMINI_MODEL no `.env`.",
            file=sys.stderr,
        )
        return _DEFAULT_GEMINI
    return nome


def build_chat_model() -> ChatGoogleGenerativeAI:
    _ensure_api_key()
    return ChatGoogleGenerativeAI(model=_modelo(), temperature=0.35)


def build_graph():
    """Grafo ReAct com prompt de sistema (Nielsen + design) e memória por `thread_id`."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    return create_react_agent(
        build_chat_model(),
        tools=[
            referencia_heuristicas_nielsen,
            guia_design_moderno_responsivo,
            executar_boletim_noticias_ex17,
        ],
        prompt=prompt,
        checkpointer=MemorySaver(),
    )


def _eh_429(exc: BaseException) -> bool:
    t = str(exc).upper()
    return "429" in t or "RESOURCE_EXHAUSTED" in t


def proxima_mensagem_utilizador(graph, mensagem: str, thread_id: str) -> None:
    config = {"configurable": {"thread_id": thread_id}}
    max_t = max(1, int(os.environ.get("GEMINI_RETRY_ATTEMPTS", "5")))
    base = max(0.5, float(os.environ.get("GEMINI_RETRY_DELAY_SEC", "2")))
    ultimo: BaseException | None = None

    for tentativa in range(max_t):
        try:
            graph.invoke({"messages": [HumanMessage(content=mensagem)]}, config)
            return
        except Exception as e:
            ultimo = e
            if _eh_429(e) and tentativa < max_t - 1:
                time.sleep(min(base * (2**tentativa), 60.0))
                continue
            break

    assert ultimo is not None
    if _eh_429(ultimo):
        raise RuntimeError(
            "API Gemini (429). Espere ou ajuste GEMINI_MODEL no `.env`. "
            f"Modelo: `{_modelo()}`."
        ) from ultimo
    raise ultimo


def obter_mensagens_do_thread(graph, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    snap = graph.get_state(config)
    if not snap or not snap.values:
        return []
    return list(snap.values.get("messages") or [])


def texto_para_mostrar(msg) -> str | None:
    if isinstance(msg, HumanMessage):
        c = msg.content
        return c if isinstance(c, str) else str(c)
    if isinstance(msg, AIMessage):
        parts: list[str] = []
        if getattr(msg, "tool_calls", None):
            nomes = [tc.get("name", "?") for tc in msg.tool_calls]
            parts.append(f"*(ferramentas: {', '.join(nomes)})*")
        c = msg.content
        if c:
            parts.append(c if isinstance(c, str) else str(c))
        return "\n\n".join(parts) if parts else None
    if isinstance(msg, ToolMessage):
        return f"**{msg.name}** →\n```\n{msg.content}\n```"
    return None
