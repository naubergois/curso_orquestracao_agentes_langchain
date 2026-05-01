"""PostgreSQL — processos jurídicos (dados fictícios) para RAG híbrido com PDFs no Chroma.

Variável `DATABASE_URL` (ou `EX09_DATABASE_URL`). Em Docker Compose do ex. 9 pré-defin-se
`postgresql://curso:curso@db:5432/juridico`.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

_STOP_PT = frozenset(
    "de da do dos das em um uma uns umas o a os as e ou que como qual quais "
    "é são foi foram para com sem se há neste nesta pelo pela pelos pelas "
    "ao aos à às doutro doutra um uma este esta estes estas".split()
)


def database_url() -> str:
    u = (
        os.environ.get("EX09_DATABASE_URL")
        or os.environ.get("DATABASE_URL")
        or ""
    ).strip()
    if u:
        return u
    port = (os.environ.get("EX09_POSTGRES_PORT") or "5434").strip() or "5434"
    return f"postgresql://curso:curso@127.0.0.1:{port}/juridico"


def conectar() -> psycopg2.extensions.connection:
    return psycopg2.connect(database_url(), connect_timeout=10)


def _palavras_chave(pergunta: str) -> list[str]:
    raw = re.split(r"[^\wáàâãéèêíìîóòôõúùûç]+", pergunta.lower())
    out: list[str] = []
    for p in raw:
        if len(p) < 3 or p in _STOP_PT:
            continue
        out.append(p)
    return out[:12]


def _executar_sql_script(conn: psycopg2.extensions.connection, path: Path) -> None:
    texto = path.read_text(encoding="utf-8")
    linhas = []
    for line in texto.splitlines():
        s = line.strip()
        if s.startswith("--"):
            continue
        linhas.append(line)
    partes = [p.strip() for p in "\n".join(linhas).split(";") if p.strip()]
    with conn.cursor() as cur:
        for stmt in partes:
            cur.execute(stmt)


def buscar_processos_para_contexto(pergunta: str, *, limite: int = 5) -> list[dict[str, Any]]:
    """Devolve processos relevantes + nomes dos PDFs anexos (ligação ao RAG nos excertos)."""
    terms = _palavras_chave(pergunta)
    sql_base = """
        SELECT
            p.id,
            p.numero,
            p.tribunal,
            p.tipo_acao,
            p.estado,
            p.data_distribuicao,
            p.partes,
            p.objeto,
            p.sumario_factual,
            p.valor_causa,
            p.temas,
            coalesce(string_agg(DISTINCT a.nome_ficheiro, ', ' ORDER BY a.nome_ficheiro), '') AS pdfs_anexo
        FROM processos p
        LEFT JOIN processo_anexos_pdf a ON a.processo_id = p.id
    """
    params: list[Any] = []
    if terms:
        conds: list[str] = []
        for t in terms:
            conds.append(
                "("
                "p.objeto ILIKE %s OR p.partes ILIKE %s OR p.temas ILIKE %s "
                "OR p.tipo_acao ILIKE %s OR p.sumario_factual ILIKE %s OR p.numero ILIKE %s"
                ")"
            )
            like = f"%{t}%"
            params.extend([like] * 6)
        sql = (
            sql_base
            + " WHERE "
            + " OR ".join(conds)
            + " GROUP BY p.id ORDER BY p.data_distribuicao DESC NULLS LAST LIMIT %s"
        )
        tu_lim = list(params) + [limite]
    else:
        sql = (
            sql_base
            + " GROUP BY p.id ORDER BY p.id ASC LIMIT %s"
        )
        tu_lim = [limite]

    with conectar() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, tu_lim)
            return list(cur.fetchall())


def formatar_processos_para_prompt(linhas: list[dict[str, Any]]) -> str:
    if not linhas:
        return "(Nenhum processo coincidente na base PostgreSQL; use apenas os excertos PDF.)"
    blocos: list[str] = []
    for r in linhas:
        pdf = (r.get("pdfs_anexo") or "").strip()
        valor = r.get("valor_causa")
        valor_s = f"{valor:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".") if valor is not None else "—"
        data = r.get("data_distribuicao")
        data_s = data.isoformat() if data else "—"
        blocos.append(
            "\n".join(
                [
                    f"• **Processo** `{r.get('numero', '?')}` | **Tribunal:** {r.get('tribunal', '?')}",
                    f"  - **Tipo / estado:** {r.get('tipo_acao', '?')} | {r.get('estado', '?')}",
                    f"  - **Distribuição:** {data_s} | **Valor da causa (ilustrativo):** {valor_s}",
                    f"  - **Partes:** {r.get('partes', '')}",
                    f"  - **Objeto:** {r.get('objeto', '')}",
                    f"  - **Sumário factual:** {r.get('sumario_factual') or '—'}",
                    f"  - **Temas (glossário):** {r.get('temas') or '—'}",
                    f"  - **PDFs pedagógicos associados (metadado `source` no Chroma):** {pdf or '—'}",
                ]
            )
        )
    return "=== Dados estruturados (PostgreSQL) — processos fictícios para estudo ===\n" + "\n\n".join(
        blocos
    )


def contexto_sql_para_rag(pergunta: str, *, limite: int = 5) -> str:
    return formatar_processos_para_prompt(buscar_processos_para_contexto(pergunta, limite=limite))


def garantir_esquema_e_seed_minimo() -> None:
    """Cria tabelas e insere dados de demonstração se `processos` estiver vazio (ex.: Python local sem Docker)."""
    root = Path(__file__).resolve().parent
    schema = root / "init_db" / "01_schema.sql"
    seed = root / "init_db" / "02_seed.sql"
    if not schema.is_file():
        return
    conn = conectar()
    try:
        conn.autocommit = True
        _executar_sql_script(conn, schema)
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM processos")
            n = cur.fetchone()[0]
        if n == 0 and seed.is_file():
            _executar_sql_script(conn, seed)
    finally:
        conn.close()
