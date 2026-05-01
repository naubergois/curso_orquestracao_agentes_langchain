"""Exemplo: SystemMessage + HumanMessage com LangChain + Gemini (sem UI, adequado a Docker).

A mensagem humana pode vir dos argumentos da linha de comandos ou da variável
`EXAMPLE_USER_MESSAGE` no ambiente.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


def _ensure_api_key() -> None:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        print(
            "Erro: defina GOOGLE_API_KEY ou GEMINI_API_KEY no `.env` na raiz do repositório.",
            file=sys.stderr,
        )
        sys.exit(1)
    os.environ.setdefault("GOOGLE_API_KEY", key)


_DEFAULT_GEMINI = "gemini-2.0-flash"


def _modelo() -> str:
    nome = (os.environ.get("GEMINI_MODEL") or _DEFAULT_GEMINI).strip() or _DEFAULT_GEMINI
    base = nome.removeprefix("models/")
    if base.startswith("gemini-1.5"):
        print(
            "Aviso: modelos `gemini-1.5*` não são usados neste curso → "
            f"`{_DEFAULT_GEMINI}`. Atualize GEMINI_MODEL no `.env`.",
            file=sys.stderr,
        )
        return _DEFAULT_GEMINI
    return nome


def _texto_utilizador() -> str:
    arg = " ".join(sys.argv[1:]).strip()
    if arg:
        return arg
    return (
        os.environ.get("EXAMPLE_USER_MESSAGE", "").strip()
        or "Diz em uma frase por que o system prompt influencia o estilo da resposta."
    )


def _eh_429(exc: BaseException) -> bool:
    t = str(exc).upper()
    return "429" in t or "RESOURCE_EXHAUSTED" in t


def main() -> None:
    _load_local_env()
    _ensure_api_key()

    llm = ChatGoogleGenerativeAI(model=_modelo(), temperature=0.2)
    mensagens = [
        SystemMessage(
            content=(
                "És um assistente didático. Responde sempre em português europeu, "
                "em no máximo duas frases curtas. Usa tom formal mas amigável."
            )
        ),
        HumanMessage(content=_texto_utilizador()),
    ]

    max_t = max(1, int(os.environ.get("GEMINI_RETRY_ATTEMPTS", "5")))
    base = max(0.5, float(os.environ.get("GEMINI_RETRY_DELAY_SEC", "2")))
    ultimo: BaseException | None = None

    for tentativa in range(max_t):
        try:
            res: AIMessage = llm.invoke(mensagens)
            texto = res.content if isinstance(res.content, str) else str(res.content)
            print(texto)
            return
        except Exception as e:
            ultimo = e
            if _eh_429(e) and tentativa < max_t - 1:
                time.sleep(min(base * (2**tentativa), 60.0))
                continue
            break

    assert ultimo is not None
    if _eh_429(ultimo):
        print(
            f"Erro 429 (quota). Modelo: `{_modelo()}`. Tente mais tarde ou altere GEMINI_MODEL.",
            file=sys.stderr,
        )
        sys.exit(2)
    print(f"Erro: {ultimo}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
