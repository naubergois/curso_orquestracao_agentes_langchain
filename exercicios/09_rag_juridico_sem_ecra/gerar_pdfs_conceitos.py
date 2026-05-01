"""Gera PDFs pedagógicos com conceitos jurídicos (PT-PT) para o exercício 9 (RAG).

Material **fictício** para demonstração técnica; não é aconselhamento jurídico.
Usa ReportLab; ficheiros gravados em `pdf_fontes/` (criar pasta antes, se necessário).
"""

from __future__ import annotations

import html
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

AVISO = (
    "<i>Documento gerado para fins pedagógicos do curso. Conteúdo simplificado e fictício; "
    "não substitui consulta a profissional do Direito nem fontes oficiais.</i>"
)


def _conceitos() -> list[tuple[str, str]]:
    """(nome_ficheiro_slug, corpo em HTML simples para Paragraph)."""
    return [
        (
            "negocio_juridico",
            """
            <b>Negócio jurídico (noção geral)</b><br/><br/>
            Designa-se por negócio jurídico a declaração ou conjunto de declarações de vontade
            que visa produzir efeitos jurídicos. Em sistemas codificados, é comum distinguir-se
            entre negócios bilaterais (contratos, em que há consentimento recíproco) e unilaterais
            (como o testamento ou a renúncia, conforme o ordenamento).<br/><br/>
            Requisitos típicos discutidos na dogmática: capacidade das partes, legitimidade
            do objecto e da forma (quando prescrita), e existência de consentimento livre e informado.
            """,
        ),
        (
            "contrato",
            """
            <b>Contrato — celebração e liberdade contratual</b><br/><br/>
            O contrato é frequentemente definido como acordo de duas ou mais vontades com o fim
            de constituir obrigações. A liberdade contratual permite às partes fixar conteúdos
            dentro dos limites legais e da ordem pública. Cláusulas gerais e condições contratuais
            impostas unilateralmente suscitam questões de transparência e equilíbrio entre partes
            desiguais.<br/><br/>
            Mecanismos como a nulidade, a anulabilidade ou a revisão podem intervir quando
            são violados requisitos essenciais ou valores protegidos.
            """,
        ),
        (
            "responsabilidade_civil",
            """
            <b>Responsabilidade civil (visão introdutória)</b><br/><br/>
            A responsabilidade civil engloba, em muitos ordenamentos, obrigações de indemnizar
            decorrentes de factos ilícitos (extracontractuais) ou do incumprimento contratual
            (contractuais). A função reparatória visa, em regra, repor a vítima no estado em que
            estaria sem o dano, dentro dos limites previstos na lei.<br/><br/>
            Conceitos recorrentes: dano (patrimonial ou não patrimonial), nexo de causalidade,
            culpa ou responsabilidade objectiva, consoante o regime aplicável.
            """,
        ),
        (
            "prescricao_caducidade",
            """
            <b>Prescrição e caducidade</b><br/><br/>
            A prescrição extingue o direito de exigir o cumprimento de uma obrigação após um
            período de inacção do titular, nos termos legais. A caducidade, onde exista,
            opera extinção ou sanção pela simples fluência do prazo ou pelo incumprimento de
            um acto processual ou jurídico, consoante o caso concreto.<br/><br/>
            A distinção precisa depende sempre do código civil ou regime especial aplicável.
            """,
        ),
        (
            "boa_fe",
            """
            <b>Boa-fé nas relações jurídicas</b><br/><br/>
            A boa-fé implica lealdade e cooperação entre sujeitos de direito: proibição de
            comportamentos abusivos ou meramente oportunistas na negociação e execução de
            negócios jurídicos. Serve frequentemente de interpretação supletiva e de limite
            ao exercício de direitos subjetivos.<br/><br/>
            A concretização varia entre sistemas de “boa-fé objectiva” nas relações obrigacionais
            e âmbitos processuais específicos.
            """,
        ),
    ]


def _styles_pdf() -> tuple[ParagraphStyle, ParagraphStyle]:
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "Corpo",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        spaceAfter=8,
    )
    titulo_aviso = ParagraphStyle(
        "Aviso",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#333333"),
        spaceAfter=16,
    )
    return body, titulo_aviso


def escrever_um_pdf(directorio: Path, slug: str, corpo_html: str) -> Path:
    """Grava um PDF com o cabeçalho de aviso pedagógico e o corpo (HTML mínimo ReportLab)."""
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    body, titulo_aviso = _styles_pdf()
    path = directorio / f"{slug}.pdf"
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    story: list = [
        Paragraph(AVISO, titulo_aviso),
        Spacer(1, 0.3 * cm),
        Paragraph(corpo_html.strip(), body),
    ]
    doc.build(story)
    return path.resolve()


def escrever_pdf_texto_plano(directorio: Path, slug: str, titulo: str, texto_plano: str) -> Path:
    """Seguro para texto vindo do LLM: escapa HTML e trata parágrafos separados por linha em branco."""
    partes = [p.strip() for p in texto_plano.split("\n\n") if p.strip()]
    corpo_paras = "<br/><br/>".join(html.escape(p) for p in partes)
    corpo = f"<b>{html.escape(titulo)}</b><br/><br/>{corpo_paras}"
    return escrever_um_pdf(directorio, slug, corpo)


def gerar_todos_pdfs(directorio: Path) -> list[Path]:
    """Grava um PDF por conceito; devolve caminhos ordenados."""
    directorio = Path(directorio)
    paths: list[Path] = []
    for slug, corpo in _conceitos():
        paths.append(escrever_um_pdf(directorio, slug, corpo))
    return paths


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    out = here / "pdf_fontes"
    for p in gerar_todos_pdfs(out):
        print("Escrito:", p)
