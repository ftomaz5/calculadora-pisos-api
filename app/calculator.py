"""Regras de negócio do cálculo de material de piso.

Funções puras, sem dependência de framework — o que facilita os testes e o reuso.
"""

from __future__ import annotations

import math
from typing import Iterable

from .models import CalculoRequest, CalculoResponse, Comodo, Produto


def area_total(comodos: Iterable[Comodo]) -> float:
    """Soma a área (m²) de uma coleção de cômodos."""
    return round(sum(c.area_m2 for c in comodos), 4)


def aplicar_margem(area_m2: float, margem_pct: float) -> float:
    """Aplica a margem de perda a uma área.

    Ex.: 20 m² com 10% de perda -> 22 m².
    """
    if area_m2 <= 0:
        raise ValueError("A área deve ser positiva.")
    if margem_pct < 0:
        raise ValueError("A margem de perda não pode ser negativa.")
    return round(area_m2 * (1 + margem_pct / 100), 4)


def caixas_necessarias(area_com_perda_m2: float, m2_por_caixa: float) -> int:
    """Quantidade de caixas para cobrir a área, sempre arredondando para cima."""
    if m2_por_caixa <= 0:
        raise ValueError("m2_por_caixa deve ser positivo.")
    return math.ceil(area_com_perda_m2 / m2_por_caixa)


def pallets_necessarios(caixas: int, caixas_por_pallet: int) -> int:
    """Quantidade de pallets para acomodar as caixas, arredondando para cima."""
    if caixas_por_pallet <= 0:
        raise ValueError("caixas_por_pallet deve ser positivo.")
    return math.ceil(caixas / caixas_por_pallet)


def calcular(request: CalculoRequest, produto: Produto) -> CalculoResponse:
    """Executa o cálculo completo e devolve o detalhamento.

    Etapas:
        1. Área líquida (soma dos cômodos ou ``area_m2`` informada).
        2. Área com perda (aplica a margem).
        3. Caixas (arredonda para cima).
        4. Área comprada, pallets, peças, sobra e custo.
    """
    if request.area_m2 is not None:
        area_liquida = round(request.area_m2, 4)
    else:
        area_liquida = area_total(request.comodos or [])

    area_com_perda = aplicar_margem(area_liquida, request.margem_perda_pct)
    caixas = caixas_necessarias(area_com_perda, produto.m2_por_caixa)
    area_comprada = round(caixas * produto.m2_por_caixa, 4)
    pallets = pallets_necessarios(caixas, produto.caixas_por_pallet)
    pecas = caixas * produto.pecas_por_caixa
    sobra = round(area_comprada - area_com_perda, 4)
    custo_por_caixa = round(produto.m2_por_caixa * produto.preco_m2, 2)
    custo_total = round(caixas * custo_por_caixa, 2)

    return CalculoResponse(
        produto=produto,
        margem_perda_pct=request.margem_perda_pct,
        area_liquida_m2=area_liquida,
        area_com_perda_m2=area_com_perda,
        caixas=caixas,
        area_comprada_m2=area_comprada,
        pallets=pallets,
        pecas=pecas,
        sobra_m2=sobra,
        custo_total=custo_total,
        custo_por_caixa=custo_por_caixa,
    )
