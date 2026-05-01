"""Exercício 04 — agente com ferramentas e PostgreSQL (dados fictícios de pacientes).

Tools: listar pacientes e obter ficha. O grafo é criado com `langchain.agents.create_agent`.
O chat usa **DeepSeek** (API compatível com OpenAI) via `langchain_openai.ChatOpenAI`.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from psycopg2.extras import RealDictCursor

_MENSAGEM_SISTEMA = """És um assistente de **estudo** em português europeu. Tens acesso a
dados fictícios de pacientes numa base PostgreSQL (demonstração do curso).

Regras:
- Usa **sempre** as ferramentas `listar_pacientes` e/ou `obter_ficha_paciente` para baseares
  a resposta em dados reais da base. Não inventes valores clínicos.
- **Um paciente por análise:** quando te pedirem fatores de risco, foca-te num único `paciente_id`
  de cada vez. Não analises vários pacientes na mesma resposta salvo o utilizador pedir
  explicitamente «todos» ou «cada um».
- Quando analisares um paciente, identifica **fatores de risco** plausíveis com base nos
  campos (ex.: IMC/obesidade, tensão arterial, glicemia, perfil lipídico incluindo LDL,
  triglicerídeos e HDL, tabagismo, sedentarismo, idade, histórico familiar).
- Explica por **bullet points** claros e breves. Indica o que parece mais relevante e o que
  parece favorável.
- **Aviso obrigatório** no fim: estes dados são fictícios; a análise é só pedagógica e
  **não substitui avaliação médica**."""


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_local_env()

_DEFAULT_DEEPSEEK = "deepseek-chat"

# Nome do modelo DeepSeek após `pick_working_deepseek_llm` (mensagens de erro / diagnóstico).
_DEEPSEEK_RESOLVIDO: str | None = None


def _ensure_exercicios_on_path() -> None:
    here = Path(__file__).resolve().parent
    for p in (here, here.parent):
        if (p / "lib_llm_fallback.py").is_file():
            s = str(p)
            if s not in sys.path:
                sys.path.insert(0, s)
            return


def _modelo_efetivo() -> str:
    return _DEEPSEEK_RESOLVIDO if _DEEPSEEK_RESOLVIDO else _modelo()


def _database_url() -> str:
    url = (os.environ.get("DATABASE_URL") or "").strip()
    if url:
        return url
    return "postgresql://curso:curso@127.0.0.1:5433/pacientes"


def _conectar():
    return psycopg2.connect(_database_url(), connect_timeout=10)


def obter_ids_nomes_pacientes() -> list[tuple[int, str]]:
    """Lista (id, nome) para UI — sem passar pelo LLM."""
    try:
        with _conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, nome FROM pacientes ORDER BY id ASC")
                return [(int(r[0]), str(r[1])) for r in cur.fetchall()]
    except Exception:
        return []


def mensagem_analise_um_paciente(paciente_id: int) -> str:
    """Prompt curto: uma ficha, menos passagens modelo/ferramentas."""
    return (
        f"Chama **apenas** `obter_ficha_paciente` com paciente_id={int(paciente_id)}. "
        "Resume os **fatores de risco** deste paciente em bullet points. "
        "Não invoques `listar_pacientes` nem compares com outros. "
        "Mantém o aviso pedagógico no fim."
    )


@tool
def listar_pacientes() -> str:
    """Lista todos os pacientes: id, nome e idade. Usa primeiro para saber os ids."""
    try:
        with _conectar() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, nome, idade FROM pacientes ORDER BY id ASC"
                )
                linhas = cur.fetchall()
        return json.dumps(linhas, ensure_ascii=False, default=str)
    except Exception as e:
        return f"Erro ao listar pacientes: {e}"


@tool
def obter_ficha_paciente(paciente_id: int) -> str:
    """Obtém a ficha clínica completa (todos os campos) do paciente pelo id."""
    try:
        pid = int(paciente_id)
    except (TypeError, ValueError):
        return "Erro: paciente_id deve ser um número inteiro."
    try:
        with _conectar() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM pacientes WHERE id = %s", (pid,))
                row = cur.fetchone()
        if not row:
            return json.dumps({"erro": f"Sem paciente com id={pid}."}, ensure_ascii=False)
        return json.dumps(dict(row), ensure_ascii=False, default=str)
    except Exception as e:
        return f"Erro ao ler paciente {pid}: {e}"


def _ensure_deepseek_key() -> None:
    key = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    if not key:
        raise RuntimeError(
            "Defina DEEPSEEK_API_KEY no `.env` na raiz do repositório (exercício 4 — DeepSeek)."
        )


def _modelo() -> str:
    return (os.environ.get("DEEPSEEK_MODEL") or _DEFAULT_DEEPSEEK).strip() or _DEFAULT_DEEPSEEK


def _api_base() -> str:
    return (os.environ.get("DEEPSEEK_API_BASE") or "https://api.deepseek.com").strip().rstrip("/")


def build_chat_model() -> Any:
    global _DEEPSEEK_RESOLVIDO
    _ensure_deepseek_key()
    _ensure_exercicios_on_path()
    from lib_llm_fallback import deepseek_model_candidates, make_deepseek_chat_with_runtime_fallback

    key = os.environ["DEEPSEEK_API_KEY"].strip()
    nomes = deepseek_model_candidates(_modelo())
    _DEEPSEEK_RESOLVIDO = " → ".join(nomes)
    return make_deepseek_chat_with_runtime_fallback(
        nomes,
        api_key=key,
        base_url=_api_base(),
        temperature=0.2,
    )


def build_graph():
    return create_agent(
        build_chat_model(),
        tools=[listar_pacientes, obter_ficha_paciente],
        system_prompt=SystemMessage(content=_MENSAGEM_SISTEMA),
        checkpointer=MemorySaver(),
    )


def _eh_429(exc: BaseException) -> bool:
    """Quota ou rate limit (vários fornecedores devolvem 429)."""
    seen: set[int] = set()
    e: BaseException | None = exc
    while e is not None:
        eid = id(e)
        if eid in seen:
            break
        seen.add(eid)
        blob = f"{type(e).__name__} {e!s} {e!r}".upper()
        if any(
            token in blob
            for token in (
                "429",
                "RESOURCE_EXHAUSTED",
                "RESOURCE EXHAUSTED",
                "RATE_LIMIT",
                "RATE LIMIT",
                "QUOTA",
                "TOO MANY REQUESTS",
            )
        ):
            return True
        for attr in ("status_code", "code", "status"):
            st = getattr(e, attr, None)
            if st == 429 or (isinstance(st, str) and "429" in st):
                return True
        e = e.__cause__
    return False


def _retry_backoff_sec(tentativa: int) -> float:
    base = max(2.0, float(os.environ.get("LLM_RETRY_DELAY_SEC", os.environ.get("GEMINI_RETRY_DELAY_SEC", "5"))))
    cap = max(30.0, float(os.environ.get("LLM_RETRY_MAX_SLEEP_SEC", os.environ.get("GEMINI_RETRY_MAX_SLEEP_SEC", "120"))))
    return min(base * (2**tentativa), cap)


def proxima_mensagem_utilizador(
    graph,
    mensagem: str,
    thread_id: str,
    *,
    on_stream_step: Callable[[], None] | None = None,
) -> None:
    config = {"configurable": {"thread_id": thread_id}}
    max_t = max(1, int(os.environ.get("LLM_RETRY_ATTEMPTS", os.environ.get("GEMINI_RETRY_ATTEMPTS", "8"))))
    ultimo: BaseException | None = None

    for tentativa in range(max_t):
        try:
            stream = graph.stream(
                {"messages": [HumanMessage(content=mensagem)]},
                config,
                stream_mode="updates",
            )
            for _chunk in stream:
                if on_stream_step is not None:
                    on_stream_step()
            return
        except Exception as e:
            ultimo = e
            if _eh_429(e) and tentativa < max_t - 1:
                delay = _retry_backoff_sec(tentativa)
                print(
                    f"[API 429] nova tentativa em {delay:.1f}s "
                    f"({tentativa + 1}/{max_t})…",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(delay)
                continue
            break

    assert ultimo is not None
    if _eh_429(ultimo):
        raise RuntimeError(
            "A API respondeu **429** (limite de pedidos ou quota). "
            "(1) Espere alguns minutos; "
            "(2) use o fluxo **um paciente de cada vez**; "
            "(3) no `.env`, aumente `LLM_RETRY_ATTEMPTS` e `LLM_RETRY_DELAY_SEC` (ou as variáveis `GEMINI_RETRY_*` legadas); "
            "(4) confirme `DEEPSEEK_MODEL` e a chave em [DeepSeek](https://platform.deepseek.com). "
            f"Modelo em uso: `{_modelo_efetivo()}`."
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
        return f"🔧 `{msg.name}` → {msg.content}"
    return None
