from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_local_env()


class Parte(BaseModel):
    nome: str = Field(description="Nome completo da parte")
    tipo: Literal["contratante", "contratada", "outra"] = Field(
        description="Papel da parte no contrato"
    )
    cnpj: str | None = Field(default=None, description="CNPJ se existir no documento")
    representante: str | None = Field(
        default=None, description="Representante legal citado"
    )


class ClausulaCritica(BaseModel):
    tema: Literal[
        "objeto",
        "prazo",
        "pagamento",
        "multa",
        "rescisao",
        "foro",
        "sigilo",
        "outra",
    ]
    resumo: str = Field(description="Resumo claro da clausula em 1 frase")
    trecho_referencia: str = Field(description="Trecho literal curto do documento")


class ContratoEstruturado(BaseModel):
    tipo_documento: str
    partes: list[Parte] = Field(default_factory=list)
    data_inicio: str | None = None
    data_fim: str | None = None
    valor_mensal_brl: str | None = Field(
        default=None, description="Valor numerico em BRL, ex: 18500.00"
    )
    prazo_meses: int | None = None
    aviso_previo_dias: int | None = None
    multa_percentual: float | None = None
    juros_mensal_percentual: float | None = None
    foro: str | None = None
    clausulas_criticas: list[ClausulaCritica] = Field(default_factory=list)
    riscos_identificados: list[str] = Field(default_factory=list)
    observacoes: list[str] = Field(default_factory=list)


def _build_llm():
    from langchain_openai import ChatOpenAI

    api_key = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError(
            "Defina DEEPSEEK_API_KEY no `.env` na raiz do repositorio para executar o exercicio 14."
        )
    model = (os.environ.get("DEEPSEEK_MODEL") or "deepseek-chat").strip() or "deepseek-chat"
    base_url = (os.environ.get("DEEPSEEK_API_BASE") or "https://api.deepseek.com").strip()
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0,
    )


def extrair_estrutura(documento: str) -> ContratoEstruturado:
    llm = _build_llm()
    prompt = f"""
Voce e um analista juridico tecnico.
Extraia informacoes estruturadas do contrato abaixo.

Regras importantes:
- Use apenas informacoes que existirem de forma explicita no texto.
- Se um campo nao existir, devolva null.
- Em valor_mensal_brl, devolva apenas numero decimal com ponto.
- Em riscos_identificados, liste riscos contratuais objetivos.
- clausulas_criticas deve conter no maximo 6 itens.

DOCUMENTO:
{documento}
""".strip()
    try:
        extractor = llm.with_structured_output(ContratoEstruturado)
        return extractor.invoke(prompt)
    except Exception as exc:
        # Alguns modelos (ex.: DeepSeek em certos endpoints) rejeitam response_format
        # usado internamente por with_structured_output. Fazemos fallback para JSON.
        if "response_format" not in str(exc).lower():
            raise

    prompt_json = f"""
Voce e um analista juridico tecnico.
Extraia informacoes do contrato e devolva APENAS JSON valido.
Nao use markdown, nao use texto fora do JSON.

Use exatamente este schema (chaves em snake_case):
{{
  "tipo_documento": "string",
  "partes": [
    {{
      "nome": "string",
      "tipo": "contratante|contratada|outra",
      "cnpj": "string|null",
      "representante": "string|null"
    }}
  ],
  "data_inicio": "string|null",
  "data_fim": "string|null",
  "valor_mensal_brl": "string|null",
  "prazo_meses": "number|null",
  "aviso_previo_dias": "number|null",
  "multa_percentual": "number|null",
  "juros_mensal_percentual": "number|null",
  "foro": "string|null",
  "clausulas_criticas": [
    {{
      "tema": "objeto|prazo|pagamento|multa|rescisao|foro|sigilo|outra",
      "resumo": "string",
      "trecho_referencia": "string"
    }}
  ],
  "riscos_identificados": ["string"],
  "observacoes": ["string"]
}}

Regras:
- Use apenas dados explicitos do texto.
- Se nao existir, use null.
- valor_mensal_brl deve ser decimal com ponto (ex.: "18500.00").
- no maximo 6 itens em clausulas_criticas.

DOCUMENTO:
{documento}
""".strip()
    resposta = llm.invoke(prompt_json)
    conteudo = resposta.content if hasattr(resposta, "content") else str(resposta)
    if not isinstance(conteudo, str):
        conteudo = str(conteudo)
    conteudo = conteudo.strip()
    if conteudo.startswith("```"):
        conteudo = conteudo.strip("`")
        conteudo = conteudo.replace("json\n", "", 1).strip()
    data = json.loads(conteudo)
    return ContratoEstruturado.model_validate(data)


def analisar_contrato(estrutura: ContratoEstruturado) -> str:
    alertas: list[str] = []
    pontos_fortes: list[str] = []

    if estrutura.aviso_previo_dias is None:
        alertas.append("Contrato sem aviso previo definido para rescisao.")
    elif estrutura.aviso_previo_dias < 15:
        alertas.append("Aviso previo curto (<15 dias) pode aumentar risco operacional.")
    else:
        pontos_fortes.append("Aviso previo definido com antecedencia razoavel.")

    if estrutura.foro:
        pontos_fortes.append(f"Foro eleito explicitamente: {estrutura.foro}.")
    else:
        alertas.append("Foro nao identificado com clareza.")

    if estrutura.multa_percentual and estrutura.multa_percentual > 10:
        alertas.append("Multa contratual elevada (>10%).")
    elif estrutura.multa_percentual is not None:
        pontos_fortes.append("Multa contratual presente com percentual moderado.")

    valor = _to_decimal(estrutura.valor_mensal_brl)
    if valor is None:
        alertas.append("Valor mensal nao foi identificado de forma estruturada.")
    elif valor > Decimal("100000"):
        alertas.append("Contrato com valor mensal alto; recomenda-se dupla validacao juridica.")
    else:
        pontos_fortes.append("Valor mensal identificado para controlo financeiro.")

    riscos_llm = estrutura.riscos_identificados[:]
    if not riscos_llm:
        alertas.append("Nenhum risco identificado pelo modelo; requer revisao humana.")

    linhas: list[str] = []
    linhas.append("Analise automatica do contrato")
    linhas.append("")
    linhas.append("Pontos fortes:")
    for p in pontos_fortes or ["- Nao identificados automaticamente."]:
        linhas.append(f"- {p}")

    linhas.append("")
    linhas.append("Alertas:")
    for a in alertas or ["- Sem alertas relevantes no baseline automatico."]:
        linhas.append(f"- {a}")

    if riscos_llm:
        linhas.append("")
        linhas.append("Riscos extraidos:")
        for r in riscos_llm:
            linhas.append(f"- {r}")

    return "\n".join(linhas)


def _to_decimal(value: str | None) -> Decimal | None:
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    caminho_documento = base_dir / "documento_juridico_exemplo.txt"
    documento = caminho_documento.read_text(encoding="utf-8")

    estrutura = extrair_estrutura(documento)
    analise = analisar_contrato(estrutura)

    print("\n=== DADOS ESTRUTURADOS (Pydantic) ===\n")
    print(estrutura.model_dump_json(indent=2, ensure_ascii=False))
    print("\n=== ANALISE ===\n")
    print(analise)


if __name__ == "__main__":
    main()
