"""Listagem de modelos e *fallback* entre nomes (Gemini via Google GenAI, DeepSeek via API OpenAI-compatível).

- **Em tempo de execução:** `make_gemini_chat_with_runtime_fallback` e `make_deepseek_chat_with_runtime_fallback`
  usam `Runnable.with_fallbacks` do LangChain — a **cada** `invoke`, se o primeiro modelo falhar com
  quota / nome inválido / etc., tenta-se o seguinte automaticamente.
- **Arranque opcional:** `pick_working_gemini_llm` / `pick_working_deepseek_llm` fazem *smoke test* até um
  nome responder (útil para diagnóstico); não substituem o fallback em cada cadeia se só o primeiro
  nome for usado sem `with_fallbacks`.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from collections.abc import Sequence
from typing import Any

_DEFAULT_GEMINI_FALLBACKS: tuple[str, ...] = (
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
)

_DEFAULT_DEEPSEEK_FALLBACKS: tuple[str, ...] = ("deepseek-chat", "deepseek-reasoner")


def normalize_gemini_model_name(name: str) -> str:
    n = (name or "").strip()
    if n.startswith("models/"):
        n = n[len("models/") :]
    return n


def _parse_csv_models(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]


def gemini_model_candidates(
    *,
    primary: str | None = None,
    ex05: bool = False,
) -> list[str]:
    """Ordem: modelo primário (argumento ou env), `GEMINI_MODEL_FALLBACKS`, predefinições 2.x (sem duplicar)."""
    p = (primary or "").strip()
    if not p:
        if ex05:
            p = (
                os.environ.get("GEMINI_MODEL_EX05")
                or os.environ.get("GEMINI_MODEL")
                or "gemini-2.0-flash"
            ).strip()
        else:
            p = (os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").strip()
    p = normalize_gemini_model_name(p)
    if p.removeprefix("models/").startswith("gemini-1.5"):
        p = "gemini-2.0-flash"

    merged: list[str] = []
    seen: set[str] = set()

    def add(x: str) -> None:
        n = normalize_gemini_model_name(x)
        if not n or n in seen:
            return
        if n.startswith("gemini-1.5"):
            return
        seen.add(n)
        merged.append(n)

    add(p)
    for x in _parse_csv_models(os.environ.get("GEMINI_MODEL_FALLBACKS")):
        add(x)
    for x in _DEFAULT_GEMINI_FALLBACKS:
        add(x)
    return merged


def deepseek_model_candidates(primary: str | None = None) -> list[str]:
    p = (primary or os.environ.get("DEEPSEEK_MODEL") or "deepseek-chat").strip() or "deepseek-chat"
    merged: list[str] = []
    seen: set[str] = set()

    def add(x: str) -> None:
        n = (x or "").strip()
        if not n or n in seen:
            return
        seen.add(n)
        merged.append(n)

    add(p)
    for x in _parse_csv_models(os.environ.get("DEEPSEEK_MODEL_FALLBACKS")):
        add(x)
    for x in _DEFAULT_DEEPSEEK_FALLBACKS:
        add(x)
    return merged


def exc_suggests_try_other_model(exc: BaseException) -> bool:
    """Indica se vale a pena tentar **outro** nome de modelo (não outra chave nem patch de rede)."""
    tokens = (
        "404",
        "NOT_FOUND",
        "NOT FOUND",
        "INVALID_ARGUMENT",
        "MODEL",
        "DOES NOT EXIST",
        "NOT_SUPPORT",
        "PERMISSION_DENIED",
        "403",
        "429",
        "RESOURCE_EXHAUSTED",
        "RESOURCE EXHAUSTED",
        "UNAVAILABLE",
        "FAILED_PRECONDITION",
    )
    seen: set[int] = set()
    e: BaseException | None = exc
    while e is not None:
        if id(e) in seen:
            break
        seen.add(id(e))
        blob = f"{type(e).__name__} {e!s} {e!r}".upper()
        if any(t in blob for t in tokens):
            return True
        for attr in ("status_code", "code", "status"):
            st = getattr(e, attr, None)
            if st in (403, 404, 429):
                return True
            if isinstance(st, str) and any(x in st for x in ("404", "429", "RESOURCE")):
                return True
        e = e.__cause__
    return False


def list_gemini_text_models(*, api_key: str | None = None) -> list[str]:
    """Lista nomes curtos (`gemini-…`) adequados a `ChatGoogleGenerativeAI`, via SDK `google.genai`."""
    key = (api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("Defina GOOGLE_API_KEY ou GEMINI_API_KEY para listar modelos Gemini.")

    try:
        from google import genai  # type: ignore[import-untyped]
    except ImportError as e:
        raise RuntimeError(
            "Pacote `google-genai` não disponível (vem com `langchain-google-genai`)."
        ) from e

    client = genai.Client(api_key=key)
    out: list[str] = []

    for m in client.models.list():
        raw = getattr(m, "name", "") or ""
        short = normalize_gemini_model_name(raw)
        if not short or "gemini" not in short.lower():
            continue
        low = short.lower()
        if any(x in low for x in ("embedding", "embed", "tts", "imagen", "veo")):
            continue
        methods = getattr(m, "supported_generation_methods", None)
        if methods is not None:
            flat = " ".join(str(x) for x in methods).upper()
            if "GENERATECONTENT" not in flat and "GENERATE_CONTENT" not in flat:
                continue
        elif not (short.startswith("gemini-") or short.startswith("gemma-")):
            continue
        out.append(short)

    return sorted(set(out))


def list_deepseek_model_ids(*, api_key: str, base_url: str) -> list[str]:
    """Chama `GET {base}/v1/models` (API compatível com OpenAI)."""
    root = base_url.rstrip("/")
    url = f"{root}/v1/models"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"DeepSeek list models HTTP {e.code}: {body[:500]}") from e

    data = json.loads(raw)
    ids: list[str] = []
    for row in data.get("data") or []:
        mid = row.get("id")
        if isinstance(mid, str) and mid.strip():
            ids.append(mid.strip())
    return sorted(set(ids))


def make_gemini_chat_with_runtime_fallback(
    model_names: Sequence[str],
    *,
    temperature: float = 0.3,
    google_api_key: str | None = None,
    **kwargs: Any,
) -> Any:
    """Vários `ChatGoogleGenerativeAI` em cadeia via `with_fallbacks` — cada `invoke` tenta o seguinte se falhar."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    key = (
        google_api_key
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or ""
    ).strip()
    names = [normalize_gemini_model_name(n) for n in model_names if normalize_gemini_model_name(n)]
    if not names:
        raise ValueError("Lista de modelos Gemini vazia.")
    llms = [
        ChatGoogleGenerativeAI(
            model=n,
            temperature=temperature,
            google_api_key=key or None,
            **kwargs,
        )
        for n in names
    ]
    first, *rest = llms
    return first if not rest else first.with_fallbacks(rest)


def make_deepseek_chat_with_runtime_fallback(
    model_names: Sequence[str],
    *,
    api_key: str,
    base_url: str,
    temperature: float = 0.2,
    **kwargs: Any,
) -> Any:
    """Vários `ChatOpenAI` (DeepSeek) via `with_fallbacks`."""
    from langchain_openai import ChatOpenAI

    root = base_url.rstrip("/")
    key = api_key.strip()
    names = [(n or "").strip() for n in model_names if (n or "").strip()]
    if not names:
        raise ValueError("Lista de modelos DeepSeek vazia.")
    llms = [
        ChatOpenAI(model=n, temperature=temperature, api_key=key, base_url=root, **kwargs)
        for n in names
    ]
    first, *rest = llms
    return first if not rest else first.with_fallbacks(rest)


def pick_working_gemini_llm(
    model_names: Sequence[str],
    *,
    temperature: float = 0.3,
    test_invoke: bool | None = None,
    test_human_msg: str = "Responde unicamente com a palavra: ok.",
) -> tuple[Any, str]:
    """Instancia `ChatGoogleGenerativeAI`; opcionalmente faz um `invoke` mínimo até um modelo funcionar."""
    from langchain_core.messages import HumanMessage
    from langchain_google_genai import ChatGoogleGenerativeAI

    if test_invoke is None:
        test_invoke = os.environ.get("LLM_FALLBACK_SKIP_SMOKE_TEST", "").strip() not in (
            "1",
            "true",
            "yes",
        )

    last: BaseException | None = None
    for raw in model_names:
        name = normalize_gemini_model_name(raw)
        if not name:
            continue
        llm = ChatGoogleGenerativeAI(model=name, temperature=temperature)
        if not test_invoke:
            return llm, name
        try:
            llm.invoke([HumanMessage(content=test_human_msg)])
            return llm, name
        except Exception as e:
            last = e
            if not exc_suggests_try_other_model(e):
                raise
            print(
                f"[lib_llm_fallback] Gemini `{name}` falhou; a tentar seguinte modelo… ({e!s})",
                file=sys.stderr,
                flush=True,
            )
    msg = "Nenhum modelo Gemini da lista respondeu. Espere se vir 429; verifique `GEMINI_MODEL*` e a lista de modelos (exercício 5)."
    raise RuntimeError(msg) from last


def pick_working_deepseek_llm(
    model_names: Sequence[str],
    *,
    api_key: str,
    base_url: str,
    temperature: float = 0.2,
    test_invoke: bool | None = None,
    test_human_msg: str = "Responde unicamente: ok.",
) -> tuple[Any, str]:
    """Instancia `ChatOpenAI` (DeepSeek); *smoke test* opcional entre nomes."""
    from langchain_core.messages import HumanMessage
    from langchain_openai import ChatOpenAI

    if test_invoke is None:
        test_invoke = os.environ.get("LLM_FALLBACK_SKIP_SMOKE_TEST", "").strip() not in (
            "1",
            "true",
            "yes",
        )

    key = api_key.strip()
    root = base_url.rstrip("/")
    last: BaseException | None = None
    for name in model_names:
        n = (name or "").strip()
        if not n:
            continue
        llm = ChatOpenAI(
            model=n,
            temperature=temperature,
            api_key=key,
            base_url=root,
        )
        if not test_invoke:
            return llm, n
        try:
            llm.invoke([HumanMessage(content=test_human_msg)])
            return llm, n
        except Exception as e:
            last = e
            if not exc_suggests_try_other_model(e):
                raise
            print(
                f"[lib_llm_fallback] DeepSeek `{n}` falhou; a tentar seguinte modelo… ({e!s})",
                file=sys.stderr,
                flush=True,
            )
    raise RuntimeError(
        "Nenhum modelo DeepSeek da lista respondeu. Verifique `DEEPSEEK_*` e a lista `/v1/models` (exercício 5)."
    ) from last
