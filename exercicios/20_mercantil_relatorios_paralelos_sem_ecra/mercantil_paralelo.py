"""Simulação de mercantil + relatórios de estoque e de lucro/vendas em paralelo (LCEL + Pydantic)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from langchain_core.runnables import Runnable, RunnableLambda, RunnableParallel
from pydantic import BaseModel, Field, computed_field, field_validator


def _dec(x: str | float | int | Decimal) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


class ProdutoCatalogo(BaseModel):
    """Referência de preços e nomes (o mercantil compra e revende ao preço de venda sugerido)."""

    sku: str = Field(min_length=1)
    nome: str = Field(min_length=1)
    preco_compra_unitario: Decimal = Field(ge=0)
    preco_venda_unitario: Decimal = Field(ge=0)

    @field_validator("preco_compra_unitario", "preco_venda_unitario", mode="before")
    @classmethod
    def _decimais(cls, v: Any) -> Decimal:
        return _dec(v)


class LinhaCompra(BaseModel):
    sku: str
    quantidade: int = Field(ge=1)
    preco_unitario: Decimal = Field(ge=0)

    @field_validator("preco_unitario", mode="before")
    @classmethod
    def _preco(cls, v: Any) -> Decimal:
        return _dec(v)


class NotaCompra(BaseModel):
    referencia: str = Field(min_length=1)
    linhas: list[LinhaCompra] = Field(min_length=1)


class LinhaVenda(BaseModel):
    sku: str
    quantidade: int = Field(ge=1)
    preco_unitario_venda: Decimal | None = Field(
        default=None,
        ge=0,
        description="Se None, usa o preço de venda do catálogo.",
    )

    @field_validator("preco_unitario_venda", mode="before")
    @classmethod
    def _preco_v(cls, v: Any) -> Decimal | None:
        if v is None:
            return None
        return _dec(v)


class NotaVenda(BaseModel):
    referencia: str = Field(min_length=1)
    linhas: list[LinhaVenda] = Field(min_length=1)


class LinhaStockRelatorio(BaseModel):
    sku: str
    nome_produto: str
    quantidade_em_stock: int = Field(ge=0)
    preco_compra_referencia: Decimal = Field(ge=0)
    valor_em_stock: Decimal = Field(ge=0)

    @field_validator("preco_compra_referencia", "valor_em_stock", mode="before")
    @classmethod
    def _d(cls, v: Any) -> Decimal:
        return _dec(v)


class RelatorioEstoque(BaseModel):
    emitido_em: datetime
    linhas: list[LinhaStockRelatorio]
    valor_total_em_stock: Decimal = Field(ge=0)

    @field_validator("valor_total_em_stock", mode="before")
    @classmethod
    def _t(cls, v: Any) -> Decimal:
        return _dec(v)


class LinhaVendaDetalhe(BaseModel):
    referencia_nota: str
    sku: str
    nome_produto: str
    quantidade: int = Field(ge=1)
    preco_unitario_venda: Decimal = Field(ge=0)
    custo_unitario_mercadoria: Decimal = Field(ge=0)
    receita_linha: Decimal = Field(ge=0)
    custo_mercadoria_linha: Decimal = Field(ge=0)
    margem_linha: Decimal

    @field_validator(
        "preco_unitario_venda",
        "custo_unitario_mercadoria",
        "receita_linha",
        "custo_mercadoria_linha",
        "margem_linha",
        mode="before",
    )
    @classmethod
    def _money(cls, v: Any) -> Decimal:
        return _dec(v)


class RelatorioLucroVendas(BaseModel):
    emitido_em: datetime
    detalhe_por_linha: list[LinhaVendaDetalhe]
    total_receita: Decimal = Field(ge=0)
    total_custo_mercadoria_vendida: Decimal = Field(ge=0)
    lucro_bruto: Decimal

    @field_validator("total_receita", "total_custo_mercadoria_vendida", "lucro_bruto", mode="before")
    @classmethod
    def _m(cls, v: Any) -> Decimal:
        return _dec(v)


class MercantilSnapshot(BaseModel):
    """Estado congelado para os dois ramos paralelos (mesma entrada, dois relatórios)."""

    emitido_em: datetime
    catalogo: list[ProdutoCatalogo]
    stock_por_sku: dict[str, int]
    historico_vendas: list[tuple[str, LinhaVenda]]  # (referencia_nota, linha)


class Mercantil:
    """Mercantil pedagógico: catálogo, stock, compras (entrada de mercadoria) e vendas."""

    def __init__(self) -> None:
        self._catalogo: dict[str, ProdutoCatalogo] = {}
        self._stock: dict[str, int] = {}
        self._vendas: list[tuple[str, LinhaVenda]] = []

    def registar_produto(self, p: ProdutoCatalogo) -> None:
        self._catalogo[p.sku] = p
        self._stock.setdefault(p.sku, 0)

    def aplicar_compra(self, nota: NotaCompra) -> None:
        for linha in nota.linhas:
            if linha.sku not in self._catalogo:
                raise ValueError(f"SKU desconhecido na compra: {linha.sku}")
            self._stock[linha.sku] = self._stock.get(linha.sku, 0) + linha.quantidade

    def aplicar_venda(self, nota: NotaVenda) -> None:
        for linha in nota.linhas:
            if linha.sku not in self._catalogo:
                raise ValueError(f"SKU desconhecido na venda: {linha.sku}")
            disp = self._stock.get(linha.sku, 0)
            if linha.quantidade > disp:
                raise ValueError(
                    f"Stock insuficiente para {linha.sku}: pedido {linha.quantidade}, disponível {disp}."
                )
            self._stock[linha.sku] = disp - linha.quantidade
            self._vendas.append((nota.referencia, linha))

    def criar_snapshot(self) -> MercantilSnapshot:
        agora = datetime.now(timezone.utc)
        return MercantilSnapshot(
            emitido_em=agora,
            catalogo=list(self._catalogo.values()),
            stock_por_sku=dict(self._stock),
            historico_vendas=list(self._vendas),
        )


def _catalogo_dict(snapshot: MercantilSnapshot) -> dict[str, ProdutoCatalogo]:
    return {p.sku: p for p in snapshot.catalogo}


def relatorio_estoque(snapshot: MercantilSnapshot) -> RelatorioEstoque:
    cat = _catalogo_dict(snapshot)
    linhas: list[LinhaStockRelatorio] = []
    total = Decimal("0")
    for sku, p in sorted(cat.items()):
        q = int(snapshot.stock_por_sku.get(sku, 0))
        valor = _dec(q) * p.preco_compra_unitario
        total += valor
        linhas.append(
            LinhaStockRelatorio(
                sku=sku,
                nome_produto=p.nome,
                quantidade_em_stock=q,
                preco_compra_referencia=p.preco_compra_unitario,
                valor_em_stock=valor,
            )
        )
    return RelatorioEstoque(emitido_em=snapshot.emitido_em, linhas=linhas, valor_total_em_stock=total)


def relatorio_lucro_vendas(snapshot: MercantilSnapshot) -> RelatorioLucroVendas:
    cat = _catalogo_dict(snapshot)
    detalhe: list[LinhaVendaDetalhe] = []
    total_rec = Decimal("0")
    total_custo = Decimal("0")
    for ref, lv in snapshot.historico_vendas:
        p = cat[lv.sku]
        p_venda = lv.preco_unitario_venda if lv.preco_unitario_venda is not None else p.preco_venda_unitario
        receita = _dec(lv.quantidade) * p_venda
        custo = _dec(lv.quantidade) * p.preco_compra_unitario
        margem = receita - custo
        total_rec += receita
        total_custo += custo
        detalhe.append(
            LinhaVendaDetalhe(
                referencia_nota=ref,
                sku=lv.sku,
                nome_produto=p.nome,
                quantidade=lv.quantidade,
                preco_unitario_venda=p_venda,
                custo_unitario_mercadoria=p.preco_compra_unitario,
                receita_linha=receita,
                custo_mercadoria_linha=custo,
                margem_linha=margem,
            )
        )
    return RelatorioLucroVendas(
        emitido_em=snapshot.emitido_em,
        detalhe_por_linha=detalhe,
        total_receita=total_rec,
        total_custo_mercadoria_vendida=total_custo,
        lucro_bruto=total_rec - total_custo,
    )


def pipeline_relatorios_paralelos() -> Runnable:
    """LCEL: um passo gera o *snapshot*; `RunnableParallel` corre os dois relatórios em paralelo."""
    return (
        RunnableLambda(lambda loja: loja.criar_snapshot())
        | RunnableParallel(
            estoque=RunnableLambda(relatorio_estoque),
            lucro_vendas=RunnableLambda(relatorio_lucro_vendas),
        )
    )


class SaidaRelatoriosParalelos(BaseModel):
    """Opcional: modelo de topo para documentar a saída do *parallel* (útil em testes e serialização)."""

    estoque: RelatorioEstoque
    lucro_vendas: RelatorioLucroVendas

    @computed_field
    @property
    def lucro_confere_com_estoque_vendido(self) -> bool:
        return self.lucro_vendas.lucro_bruto == (
            self.lucro_vendas.total_receita - self.lucro_vendas.total_custo_mercadoria_vendida
        )
