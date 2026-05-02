"""Parser jurídico: Instructor + Gemini (saída estruturada Pydantic) em duas fases."""

from __future__ import annotations

import os
from functools import lru_cache

import instructor

from app.schemas.demanda import DemandaExtraida, ScreeningJuridico


class TextoNaoJuridicoError(Exception):
    """Texto não passou no screening jurídico."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


_SYSTEM_SCREENING = """És um filtro prévio para um escritório de advogados em **Portugal** (português europeu).

Decide se o texto descreve uma situação com **dimensão jurídica** relevante para triagem interna: contratos e incumprimento,
litígios, responsabilidade civil ou criminal genérica mencionada, direito do trabalho ou consumo, obrigações legais,
prazos processuais ou administrativos, propriedade, multas com fundamento legal, incidentes com segurança ou dados com implicações legais, etc.

Marca **texto_refere_questao_juridica = false** quando o conteúdo for claramente **não jurídico**: receitas,
piadas, código de programação sem contexto legal, spam, spam marketing genérico, lista de compras, texto aleatório,
ou quando não existir qualquer pedido ou facto suscetível de análise jurídica.

Preenche **motivo** em uma ou duas frases objetivas."""


_SYSTEM_EXTRACAO = """És analista jurídico **assistencial** (PT-PT) para triagem interna de escritório.

Extrai apenas informação **presente ou razoavelmente implícita** no texto. Não inventes nomes, valores ou prazos.

Campos:
- **tipo_demanda**: etiqueta curta (contratual, trabalhista, consumerista, administrativo, civil_geral, penal_referencia, outro).
- **partes_envolvidas**: lista de nomes ou designações explicitamente mencionados; vazio se não houver.
- **prazo**: texto curto com prazos/datas/urgência referidos; null se não existir menção útil.
- **risco** e **prioridade**: inferência **conservadora** (ex.: menção a execução, cobrança urgente, lesões → prioridade/risco maiores).
- **resumo**: 2 a 5 frases factuais; **sem** conclusões definitivas do tipo «deve ganhar o processo»; sem substituir advogado."""


def _nome_modelo() -> str:
    raw = (
        os.environ.get("GEMINI_MODEL_EX05")
        or os.environ.get("GEMINI_MODEL")
        or "gemini-2.0-flash"
    )
    return raw.replace("models/", "").strip()


@lru_cache(maxsize=1)
def _cliente_instructor():
    model = _nome_modelo()
    return instructor.from_provider(f"google/{model}")


def analisar_demanda(texto: str) -> DemandaExtraida:
    texto_limpo = texto.strip()
    client = _cliente_instructor()

    screening = client.create(
        messages=[
            {"role": "system", "content": _SYSTEM_SCREENING},
            {
                "role": "user",
                "content": f"Texto recebido para triagem:\n\n{texto_limpo}",
            },
        ],
        response_model=ScreeningJuridico,
        max_retries=2,
    )

    if not screening.texto_refere_questao_juridica:
        raise TextoNaoJuridicoError(
            screening.motivo or "Conteúdo não identificado como jurídico para triagem."
        )

    return client.create(
        messages=[
            {"role": "system", "content": _SYSTEM_EXTRACAO},
            {
                "role": "user",
                "content": (
                    "Extrai os campos pedidos a partir do texto abaixo.\n\n"
                    f"{texto_limpo}"
                ),
            },
        ],
        response_model=DemandaExtraida,
        max_retries=2,
    )
