"""API FastAPI da PromptLab Consultoria — três perfis + desafio extra (sarcástico nerd)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from app.chains.coordenacoes import DESCRICOES_MODOS, executar_coordenacao
from app.chains.promptlab_chain import gerar_resposta
from app.schemas.coordenacao import CoordenacaoEntrada, CoordenacaoSaida, ModoCoordenacao
from app.schemas.pergunta import PerfilAssistente, PerguntaEntrada, RespostaSaida


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


def _garantir_chave() -> None:
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        print(
            "Erro: defina GOOGLE_API_KEY (ou GEMINI_API_KEY) no `.env` na raiz do repositório do curso.",
            file=sys.stderr,
        )
        sys.exit(1)


_carregar_env()

app = FastAPI(
    title="PromptLab Consultoria",
    description=(
        "Perfis de system prompt + **cinco modos de coordenação multi-agente** "
        "(LangChain + Pydantic)."
    ),
    version="1.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/perfis")
def perfis() -> dict[str, list[str]]:
    return {"perfis": [p.value for p in PerfilAssistente]}


@app.get("/coordenacao/modos")
def listar_modos_coordenacao() -> dict[str, dict[str, str]]:
    return {
        "modos": {
            k: v for k, v in DESCRICOES_MODOS.items()
        },
        "valores": [m.value for m in ModoCoordenacao],
    }


@app.post("/coordenacao", response_model=CoordenacaoSaida)
def coordenacao(body: CoordenacaoEntrada) -> CoordenacaoSaida:
    try:
        return executar_coordenacao(body.modo, body.pergunta)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=(
                "Falha na coordenação multi-agente. Verifique GOOGLE_API_KEY e quota. "
                f"Detalhe: {e!s}"
            ),
        ) from e


@app.post("/responder", response_model=RespostaSaida)
def responder(body: PerguntaEntrada) -> RespostaSaida:
    try:
        texto = gerar_resposta(body.perfil, body.pergunta)
        return RespostaSaida(perfil=body.perfil.value, resposta=texto)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=(
                "Falha ao contactar o modelo. Verifique GOOGLE_API_KEY e quota. "
                f"Detalhe: {e!s}"
            ),
        ) from e


def main() -> None:
    _garantir_chave()
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    main()
