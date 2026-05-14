"""Dados fictícios de vendas e catálogo para o agente de marketing (exercício 21)."""

from __future__ import annotations

import json
from collections import defaultdict
from decimal import Decimal

from pydantic import BaseModel, Field


class ProdutoCatalogo(BaseModel):
    sku: str
    nome: str
    categoria: str
    preco_referencia_eur: Decimal = Field(ge=0)
    pitch_curto: str = Field(description="Ângulo de valor para marketing")


class LinhaVendaSim(BaseModel):
    sku: str
    unidades: int = Field(ge=1)
    receita_eur: Decimal = Field(ge=0)


# Catálogo pedagógico (marca fictícia)
CATALOGO: dict[str, ProdutoCatalogo] = {
    "CAFE500": ProdutoCatalogo(
        sku="CAFE500",
        nome="Café Torrado 500 g — linha «Amanhecer»",
        categoria="Bebidas quentes / pequeno-almoço",
        preco_referencia_eur=Decimal("4.99"),
        pitch_curto="Aroma intenso, embalagem reciclável; ideal para famílias e escritório.",
    ),
    "CHA25": ProdutoCatalogo(
        sku="CHA25",
        nome="Chá verde premium 25 saquetas",
        categoria="Bebidas quentes / pequeno-almoço",
        preco_referencia_eur=Decimal("2.89"),
        pitch_curto="Bem-estar e rotina saudável; cross-sell com mel e limão.",
    ),
    "AGUA6L": ProdutoCatalogo(
        sku="AGUA6L",
        nome="Água mineral 6×1,5 L",
        categoria="Bebidas",
        preco_referencia_eur=Decimal("3.29"),
        pitch_curto="Pack familiar; forte em volume, margem mais baixa.",
    ),
    "BOLACH400": ProdutoCatalogo(
        sku="BOLACH400",
        nome="Bolachas integrais 400 g",
        categoria="Snacks",
        preco_referencia_eur=Decimal("1.79"),
        pitch_curto="Lanche escolar e merenda; destaque nutricional moderado.",
    ),
    "ATUM3": ProdutoCatalogo(
        sku="ATUM3",
        nome="Atum posta ao natural 3×120 g",
        categoria="Mercearia salgada",
        preco_referencia_eur=Decimal("4.49"),
        pitch_curto="Proteína rápida; campanhas de receitas e refeições em 15 min.",
    ),
}

# Histórico agregado fictício (várias lojas / semanas)
_LINHAS_DEMO: list[LinhaVendaSim] = [
    LinhaVendaSim(sku="CAFE500", unidades=420, receita_eur=Decimal("2058.00")),
    LinhaVendaSim(sku="CAFE500", unidades=180, receita_eur=Decimal("880.20")),
    LinhaVendaSim(sku="CHA25", unidades=310, receita_eur=Decimal("895.90")),
    LinhaVendaSim(sku="AGUA6L", unidades=950, receita_eur=Decimal("3125.50")),
    LinhaVendaSim(sku="BOLACH400", unidades=220, receita_eur=Decimal("393.80")),
    LinhaVendaSim(sku="ATUM3", unidades=140, receita_eur=Decimal("628.60")),
    LinhaVendaSim(sku="CHA25", unidades=95, receita_eur=Decimal("274.55")),
    LinhaVendaSim(sku="BOLACH400", unidades=400, receita_eur=Decimal("716.00")),
]


def agregar_por_sku() -> dict[str, dict[str, Decimal | int]]:
    u: dict[str, int] = defaultdict(int)
    r: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for linha in _LINHAS_DEMO:
        u[linha.sku] += linha.unidades
        r[linha.sku] += linha.receita_eur
    out: dict[str, dict[str, Decimal | int]] = {}
    for sku in u:
        out[sku] = {"unidades_vendidas": u[sku], "receita_total_eur": r[sku]}
    return out


def ranking_por_unidades(limite: int = 10) -> list[dict[str, object]]:
    agg = agregar_por_sku()
    linhas: list[tuple[str, int, Decimal]] = []
    for sku, v in agg.items():
        linhas.append((sku, int(v["unidades_vendidas"]), Decimal(str(v["receita_total_eur"]))))
    linhas.sort(key=lambda x: (-x[1], -x[2]))
    resultado: list[dict[str, object]] = []
    for pos, (sku, un, rec) in enumerate(linhas[:limite], start=1):
        p = CATALOGO[sku]
        resultado.append(
            {
                "posicao": pos,
                "sku": sku,
                "nome": p.nome,
                "categoria": p.categoria,
                "unidades_vendidas": un,
                "receita_total_eur": str(rec),
            }
        )
    return resultado


def produto_mais_vendido_por_unidades() -> dict[str, object]:
    r = ranking_por_unidades(1)
    if not r:
        raise RuntimeError("Sem dados de ranking.")
    topo = r[0]
    sku = str(topo["sku"])
    p = CATALOGO[sku]
    return {
        "sku": sku,
        "nome": p.nome,
        "categoria": p.categoria,
        "preco_referencia_eur": str(p.preco_referencia_eur),
        "pitch_curto": p.pitch_curto,
        "unidades_vendidas": topo["unidades_vendidas"],
        "receita_total_eur": topo["receita_total_eur"],
    }


def ficha_produto_json(sku: str) -> str:
    sku = (sku or "").strip().upper()
    if sku not in CATALOGO:
        return json.dumps({"erro": f"SKU desconhecido: {sku}"}, ensure_ascii=False)
    p = CATALOGO[sku]
    agg = agregar_por_sku().get(sku, {"unidades_vendidas": 0, "receita_total_eur": Decimal("0")})
    payload = {
        "sku": p.sku,
        "nome": p.nome,
        "categoria": p.categoria,
        "preco_referencia_eur": str(p.preco_referencia_eur),
        "pitch_curto": p.pitch_curto,
        "unidades_vendidas_periodo": agg["unidades_vendidas"],
        "receita_total_eur_periodo": str(agg["receita_total_eur"]),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def contexto_marca_json() -> str:
    """Tom de voz e restrições pedagógicas para o agente alinhar copy."""
    return json.dumps(
        {
            "marca": "Rede «Mercado Central» (fictícia)",
            "tom_voz": "português europeu, claro, próximo, sem jargão inglês desnecessário",
            "evitar": "descontos ilegais, comparações denigrativas a concorrentes nomeados, promessas médicas",
            "canais_preferidos": ["rede social local", "email de fidelização", "cartazes loja", "folheto digital"],
            "duracao_campanha_sugerida_semanas": 4,
        },
        ensure_ascii=False,
        indent=2,
    )
