"""Exercício 00 — o mais simples possível: LangChain + Gemini, uma pergunta, uma resposta."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI


def _load_repo_dotenv() -> None:
    """Procura `.env` a subir a partir da pasta de `main.py`. No contentor só há `/app/` — variáveis vêm do Compose."""
    here = Path(__file__).resolve().parent
    for d in (here, *here.parents):
        candidate = d / ".env"
        if candidate.is_file():
            load_dotenv(candidate, override=False)
            return


if __name__ == "__main__":
    _load_repo_dotenv()

    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        print(
            "Erro: defina GOOGLE_API_KEY (ficheiro `.env` na raiz do repo ou env_file no Docker Compose).",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)
    os.environ.setdefault("GOOGLE_API_KEY", key)

    modelo = (os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").strip() or "gemini-2.0-flash"
    if modelo.removeprefix("models/").startswith("gemini-1.5"):
        print(
            "Aviso: modelos `gemini-1.5*` não são usados neste curso → `gemini-2.0-flash`. "
            "Atualiza GEMINI_MODEL no `.env`.",
            file=sys.stderr,
            flush=True,
        )
        modelo = "gemini-2.0-flash"
    print(f"Modelo: {modelo}", flush=True)
    llm = ChatGoogleGenerativeAI(model=modelo, temperature=0.2)
    print("A pedir resposta ao Gemini…", flush=True)
    res = llm.invoke([HumanMessage(content="Responde só com: Olá, mundo!")])
    texto = res.content if isinstance(res.content, str) else str(res.content)
    print("Resposta:", flush=True)
    print(texto, flush=True)
