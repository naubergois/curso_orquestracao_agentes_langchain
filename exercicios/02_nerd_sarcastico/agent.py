"""Exercício 02 — nerd sarcástico, uma mensagem de cada vez (sem histórico no modelo).

Cada chamada envia só: SystemMessage (persona) + HumanMessage (texto actual).
O Streamlit pode mostrar só o último par pergunta/resposta.
"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

PERSONA_SYSTEM = """És um nerd sarcástico que gosta de cultura geek (tech, ciência, jogos, etc.). Responde em português.
Ironia seca, sem ódio nem ataques a grupos protegidos. Zomba da ideia, não da pessoa. Respostas curtas (2–4 frases), salvo que peçam mais."""

_DEFAULT_MODELO = "gemini-2.0-flash"


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_local_env()


def _ensure_api_key() -> None:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "Defina GOOGLE_API_KEY ou GEMINI_API_KEY no `.env` na raiz do repositório."
        )
    os.environ.setdefault("GOOGLE_API_KEY", key)


def _modelo() -> str:
    return (os.environ.get("GEMINI_MODEL_EX02") or _DEFAULT_MODELO).strip() or _DEFAULT_MODELO


def _temperatura() -> float:
    raw = os.environ.get("NERD_SARCASTICO_TEMPERATURE") or os.environ.get("ANTI_COACH_TEMPERATURE", "0.75")
    return min(max(float(raw), 0.0), 2.0)


def _quota(texto: str) -> bool:
    return "429" in texto.upper() or "RESOURCE_EXHAUSTED" in texto.upper()


def responder(texto_utilizador: str) -> str:
    """Uma única troca: system + mensagem do utilizador. Sem conversa anterior."""
    _ensure_api_key()
    modelo = ChatGoogleGenerativeAI(model=_modelo(), temperature=_temperatura())
    mensagens = [SystemMessage(content=PERSONA_SYSTEM), HumanMessage(content=texto_utilizador)]

    max_t = max(1, int(os.environ.get("GEMINI_RETRY_ATTEMPTS", "5")))
    base = max(0.5, float(os.environ.get("GEMINI_RETRY_DELAY_SEC", "2")))
    ultimo: BaseException | None = None

    for tentativa in range(max_t):
        try:
            r: AIMessage = modelo.invoke(mensagens)
            return r.content if isinstance(r.content, str) else str(r.content)
        except Exception as e:
            ultimo = e
            if _quota(str(e)) and tentativa < max_t - 1:
                time.sleep(min(base * (2**tentativa), 60.0))
                continue
            break

    assert ultimo is not None
    if _quota(str(ultimo)):
        raise RuntimeError(
            "API Gemini (429). Espere ou ajuste GEMINI_MODEL_EX02 no `.env`. "
            f"Modelo: `{_modelo()}`."
        ) from ultimo
    raise ultimo
