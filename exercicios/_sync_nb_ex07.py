#!/usr/bin/env python3
"""Sincroniza `07.../exercicio_7_sem_ecra.ipynb` a partir de `07_precos_clima_cotacao/agent.py`."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
agent_p = ROOT / "exercicios/07_precos_clima_cotacao/agent.py"
agent = agent_p.read_text(encoding="utf-8")
ms = re.search(r'_MENSAGEM_SISTEMA = """(.*?)"""', agent, re.DOTALL)
if not ms:
    raise SystemExit("agent.py: _MENSAGEM_SISTEMA em falta")
ms_body = ms.group(1)
i0 = agent.index("def _http_json")
i1 = agent.index("\n\ndef _load_local_env")
tools_block = agent[i0:i1]

imports = f'''from __future__ import annotations

import ast
import hashlib
import json
import operator
import os
import sys
import time
import re
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

_USER_AGENT = "Mozilla/5.0 (compatible; CursoLangChain/1.0; +educational)"

_MS = """{ms_body}"""

'''

cell1 = imports + "\n" + tools_block

cell2 = r'''_ex = Path.cwd().resolve().parent
if str(_ex) not in sys.path:
    sys.path.insert(0, str(_ex))
from lib_llm_fallback import gemini_model_candidates, make_gemini_chat_with_runtime_fallback

key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not key:
    raise RuntimeError("Defina GOOGLE_API_KEY no `.env`.")
os.environ.setdefault("GOOGLE_API_KEY", key)

_default = "gemini-2.0-flash"
_prim = (
    os.environ.get("GEMINI_MODEL_EX07")
    or os.environ.get("GEMINI_MODEL")
    or _default
).strip() or _default
if _prim.removeprefix("models/").startswith("gemini-1.5"):
    print("Aviso: gemini-1.5* → gemini-2.0-flash")
    _prim = _default

candidatos = gemini_model_candidates(primary=_prim)
llm = make_gemini_chat_with_runtime_fallback(candidatos, temperature=0.2)
print("Modelos (ordem):", " → ".join(candidatos))

_TOOLS_NB = (
    buscar_preco_produto,
    clima_em_fortaleza,
    cotacao_dolar_em_real,
    cotacao_euro_em_real,
    wikipedia_pt_buscar,
    duckduckgo_resumo_instantaneo,
    consultar_cep_brasil,
    feriados_nacionais_brasil,
    calculadora,
    data_hora_fuso,
    converter_celsius_fahrenheit,
    extrair_urls_texto,
    hash_sha256_texto,
)

graph = create_react_agent(
    llm,
    tools=list(_TOOLS_NB),
    prompt=SystemMessage(content=_MS),
    checkpointer=MemorySaver(),
)
cfg = {"configurable": {"thread_id": "notebook-demo"}}
'''


def split_lines(s: str) -> list[str]:
    return [line + "\n" for line in s.splitlines()]

md = """# Exercício 7 — sem ecrã (agente **ReAct** + *tools* variadas)

LangGraph `create_react_agent` com **treze** ferramentas, no espírito de *toolkits* LangChain / exemplos de outros frameworks:

| Tema | Ferramentas |
|------|----------------|
| **Mercado / clima / FX** | `buscar_preco_produto`, `clima_em_fortaleza`, `cotacao_dolar_em_real`, `cotacao_euro_em_real` |
| **Conhecimento / pesquisa leve** | `wikipedia_pt_buscar` (estilo *WikipediaQueryRun*), `duckduckgo_resumo_instantaneo` (estilo DDG sem API key) |
| **Brasil estruturado** | `consultar_cep_brasil`, `feriados_nacionais_brasil` (BrasilAPI) |
| **Utilitários de agente** | `calculadora`, `data_hora_fuso`, `converter_celsius_fahrenheit`, `extrair_urls_texto`, `hash_sha256_texto` |

**Requisitos:** `GOOGLE_API_KEY`; **Internet**. Opcional: `GEMINI_MODEL_EX07`, `GEMINI_MODEL_FALLBACKS`.

A **célula 1** copia as funções de `exercicios/07_precos_clima_cotacao/agent.py` — após alterar o `agent.py`, corre `python exercicios/_sync_nb_ex07.py`.

**Streamlit:** `exercicios/07_precos_clima_cotacao/`.
"""

md2 = "### Testar uma mensagem\n\nAltera o texto em `msgs` para forçar várias *tools* (ex.: CEP + feriados + Wikipédia)."

cell3 = r'''from langchain_core.messages import HumanMessage

msgs = [HumanMessage(
    content="Qual o CEP 01310-100? Quantos graus Fahrenheit são 30 °C? Dá um feriado nacional de 2026 no Brasil."
)]
max_t = max(1, int(os.environ.get("GEMINI_RETRY_ATTEMPTS", "5")))
base = max(0.5, float(os.environ.get("GEMINI_RETRY_DELAY_SEC", "2")))
for tentativa in range(max_t):
    try:
        graph.invoke({"messages": msgs}, cfg)
        break
    except Exception as e:
        if tentativa < max_t - 1 and ("429" in str(e).upper() or "RESOURCE_EXHAUSTED" in str(e).upper()):
            time.sleep(min(base * (2**tentativa), 60.0))
            continue
        raise

snap = graph.get_state(cfg)
for m in snap.values.get("messages") or []:
    if isinstance(m, HumanMessage):
        print("👤", str(m.content)[:200])
    elif isinstance(m, AIMessage):
        if m.tool_calls:
            print("🔧", [tc.get("name") for tc in m.tool_calls])
        if m.content:
            print("🤖", str(m.content)[:500])
    elif isinstance(m, ToolMessage):
        print("📎", m.name, "→", str(m.content)[:400], "...")
'''

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": split_lines(md), "id": "c0"},
        {"cell_type": "code", "metadata": {}, "outputs": [], "execution_count": None, "source": split_lines(cell1), "id": "c1"},
        {"cell_type": "code", "metadata": {}, "outputs": [], "execution_count": None, "source": split_lines(cell2), "id": "c2"},
        {"cell_type": "markdown", "metadata": {}, "source": split_lines(md2), "id": "c3"},
        {"cell_type": "code", "metadata": {}, "outputs": [], "execution_count": None, "source": split_lines(cell3), "id": "c4"},
    ],
}

out = ROOT / "exercicios/07_precos_clima_cotacao_sem_ecra/exercicio_7_sem_ecra.ipynb"
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("Escrito:", out.relative_to(ROOT))
