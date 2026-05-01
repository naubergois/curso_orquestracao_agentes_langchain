"""Exercício 01 — o mínimo possível com LangChain + Gemini.

Ideia em três passos (é tudo o que este ficheiro faz):

1. Carregar a chave `GOOGLE_API_KEY` do ficheiro `.env` na raiz do repositório.
2. Criar um `ChatGoogleGenerativeAI` — o objeto que representa o modelo na API Gemini.
3. Chamar `modelo.invoke(mensagens)` — envia o histórico (lista de mensagens) e recebe
   uma `AIMessage` com o texto da resposta.

Não há grafo, não há ferramentas, não há “agente ReAct”: só conversa com o modelo,
como base para os exercícios seguintes.
"""

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI


def _load_local_env() -> None:
    """Procura um ficheiro `.env` nesta pasta ou nas pastas acima e carrega as variáveis."""
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
            "Defina GOOGLE_API_KEY ou GEMINI_API_KEY no `.env` ou no ambiente "
            "(chave em https://aistudio.google.com/apikey)."
        )
    os.environ.setdefault("GOOGLE_API_KEY", key)


def _modelo_configurado() -> str:
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


def build_chat_model() -> ChatGoogleGenerativeAI:
    """Instancia o modelo Gemini usado neste exercício."""
    _ensure_api_key()
    return ChatGoogleGenerativeAI(
        model=_modelo_configurado(),
        temperature=0.2,
    )


def _eh_erro_limite_quota(exc: BaseException) -> bool:
    texto = str(exc).upper()
    return "429" in texto or "RESOURCE_EXHAUSTED" in texto


def mensagens_a_partir_do_historico(
    turnos: list[dict[str, str]],
) -> list[BaseMessage]:
    """Converte o histórico simples da UI em mensagens LangChain para o modelo."""
    saida: list[BaseMessage] = []
    for t in turnos:
        role, content = t["role"], t["content"]
        if role == "user":
            saida.append(HumanMessage(content=content))
        elif role == "assistant":
            saida.append(AIMessage(content=content))
    return saida


def run_chat_turn(
    turnos: list[dict[str, str]],
    model: ChatGoogleGenerativeAI | None = None,
) -> tuple[list[dict[str, str]], str]:
    """Recebe o histórico *já* com a última mensagem do utilizador; devolve histórico + texto da resposta.

    O histórico em `turnos` usa apenas `{"role": "user"|"assistant", "content": "..."}` para
    o Streamlit serializar o estado sem surpresas.

    Passa o mesmo `model` entre turnos (ex.: `st.session_state`) para não recriar o cliente HTTP
    a cada mensagem. Sem `model`, cria um `ChatGoogleGenerativeAI` novo (útil em notebooks).
    """
    messages = mensagens_a_partir_do_historico(turnos)
    if model is None:
        model = build_chat_model()
    max_tentativas = max(1, int(os.environ.get("GEMINI_RETRY_ATTEMPTS", "5")))
    atraso_base = max(0.5, float(os.environ.get("GEMINI_RETRY_DELAY_SEC", "2")))

    ultimo_erro: BaseException | None = None
    for tentativa in range(max_tentativas):
        try:
            answer: AIMessage = model.invoke(messages)
            text = answer.content if isinstance(answer.content, str) else str(answer.content)
            novo = [
                *turnos,
                {"role": "assistant", "content": text},
            ]
            return novo, text
        except Exception as e:
            ultimo_erro = e
            if _eh_erro_limite_quota(e) and tentativa < max_tentativas - 1:
                time.sleep(min(atraso_base * (2**tentativa), 60.0))
                continue
            break

    assert ultimo_erro is not None
    if _eh_erro_limite_quota(ultimo_erro):
        modelo = _modelo_configurado()
        raise RuntimeError(
            "A API Gemini recusou o pedido por limite de quota ou pedidos demasiado frequentes (429). "
            "Tente daqui a alguns minutos, faça menos mensagens seguidas, ou no `.env` use outro modelo, "
            f"por exemplo no `.env`: GEMINI_MODEL=gemini-2.0-flash ou GEMINI_MODEL=gemini-2.5-flash "
            f"(agora: `{modelo}`). "
            "Detalhes: https://ai.google.dev/gemini-api/docs/rate-limits"
        ) from ultimo_erro
    raise ultimo_erro


def append_user_turn(turnos: list[dict[str, str]], text: str) -> list[dict[str, str]]:
    """Acrescenta a mensagem do utilizador ao histórico."""
    return [*turnos, {"role": "user", "content": text}]
