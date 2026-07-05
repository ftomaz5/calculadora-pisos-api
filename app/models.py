"""Modelos de dados (schemas) da API, validados com Pydantic v2."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class Produto(BaseModel):
    """Representa um produto do catálogo (uma referência de piso)."""

    id: str = Field(..., description="Identificador único do produto.")
    nome: str = Field(..., description="Nome comercial do produto.")
    linha: str = Field(..., description="Linha/coleção a que o produto pertence.")
    formato: str = Field(..., description="Formato da peça, ex: '60x60'.")
    m2_por_caixa: float = Field(..., gt=0, description="Metros quadrados que uma caixa cobre.")
    pecas_por_caixa: int = Field(..., gt=0, description="Quantidade de peças em cada caixa.")
    caixas_por_pallet: int = Field(..., gt=0, description="Quantidade de caixas em cada pallet.")
    preco_m2: float = Field(..., gt=0, description="Preço de venda por metro quadrado (R$).")


class Comodo(BaseModel):
    """Um ambiente a ser revestido, informado por comprimento e largura."""

    nome: Optional[str] = Field(default=None, description="Nome do cômodo, ex: 'Sala'.")
    comprimento_m: float = Field(..., gt=0, le=1000, description="Comprimento em metros.")
    largura_m: float = Field(..., gt=0, le=1000, description="Largura em metros.")

    @property
    def area_m2(self) -> float:
        """Área do cômodo em metros quadrados."""
        return self.comprimento_m * self.largura_m


class CalculoRequest(BaseModel):
    """Entrada do cálculo.

    O usuário informa o produto, a margem de perda e a área — seja pela lista de
    cômodos (comprimento x largura) ou diretamente por `area_m2`.
    """

    produto_id: str = Field(..., description="ID do produto do catálogo.")
    comodos: Optional[List[Comodo]] = Field(
        default=None, description="Lista de cômodos a revestir."
    )
    area_m2: Optional[float] = Field(
        default=None, gt=0, description="Área total em m² (alternativa à lista de cômodos)."
    )
    margem_perda_pct: float = Field(
        default=10.0,
        ge=0,
        le=100,
        description="Margem de perda em % (recortes/quebras). Padrão de mercado: 10%.",
    )

    @model_validator(mode="after")
    def _validar_area(self) -> "CalculoRequest":
        tem_comodos = bool(self.comodos)
        tem_area = self.area_m2 is not None
        if not tem_comodos and not tem_area:
            raise ValueError("Informe 'comodos' ou 'area_m2'.")
        if tem_comodos and tem_area:
            raise ValueError("Informe apenas 'comodos' OU 'area_m2', não os dois.")
        return self


class CalculoResponse(BaseModel):
    """Resultado detalhado do cálculo de material."""

    produto: Produto
    margem_perda_pct: float
    area_liquida_m2: float = Field(..., description="Área real dos ambientes, sem perda.")
    area_com_perda_m2: float = Field(..., description="Área considerando a margem de perda.")
    caixas: int = Field(..., description="Caixas necessárias (arredondado para cima).")
    area_comprada_m2: float = Field(..., description="Área efetivamente comprada (caixas inteiras).")
    pallets: int = Field(..., description="Pallets necessários (arredondado para cima).")
    pecas: int = Field(..., description="Total de peças.")
    sobra_m2: float = Field(..., description="Sobra de material em relação à área com perda.")
    custo_total: float = Field(..., description="Custo total estimado (R$).")
    custo_por_caixa: float = Field(..., description="Custo de uma caixa (R$).")


class ErrorResponse(BaseModel):
    """Formato padrão de erro."""

    detail: str


class PrevisaoRequest(BaseModel):
    """Entrada para a previsão de demanda mensal de um produto."""

    produto_id: str = Field(..., description="ID do produto do catálogo.")
    mes: int = Field(..., ge=1, le=12, description="Mês de referência (1=jan ... 12=dez).")
    indice_mercado: float = Field(
        default=100.0,
        ge=50,
        le=200,
        description="Índice do mercado de construção (100 = base/média).",
    )
    promo: bool = Field(default=False, description="Se o produto está em promoção no mês.")


class PrevisaoResponse(BaseModel):
    """Resultado da previsão de demanda."""

    produto: Produto
    mes: int
    indice_mercado: float
    promo: bool
    demanda_prevista_m2: float = Field(..., description="Demanda mensal prevista (m²).")
    unidade: str = "m²/mês"
