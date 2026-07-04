"""Testes das regras de negócio (funções puras de cálculo)."""

import math

import pytest

from app.calculator import (
    aplicar_margem,
    area_total,
    caixas_necessarias,
    calcular,
    pallets_necessarios,
)
from app.catalog import obter_produto
from app.models import CalculoRequest, Comodo


def test_area_total_soma_comodos():
    comodos = [Comodo(comprimento_m=5, largura_m=4), Comodo(comprimento_m=3, largura_m=2)]
    assert area_total(comodos) == 26.0


def test_aplicar_margem_padrao():
    assert aplicar_margem(20.0, 10.0) == 22.0


def test_aplicar_margem_zero():
    assert aplicar_margem(20.0, 0.0) == 20.0


def test_aplicar_margem_area_invalida():
    with pytest.raises(ValueError):
        aplicar_margem(0, 10)


def test_aplicar_margem_negativa():
    with pytest.raises(ValueError):
        aplicar_margem(10, -5)


def test_caixas_arredonda_para_cima():
    # 22 m² / 2.16 m² por caixa = 10.18 -> 11 caixas
    assert caixas_necessarias(22.0, 2.16) == 11


def test_caixas_exatas_nao_arredondam():
    assert caixas_necessarias(21.6, 2.16) == 10


def test_pallets_arredonda_para_cima():
    assert pallets_necessarios(50, 48) == 2
    assert pallets_necessarios(48, 48) == 1


def test_calcular_resultado_completo():
    produto = obter_produto("urban-stone-cimento-60x60")
    req = CalculoRequest(
        produto_id=produto.id,
        comodos=[Comodo(comprimento_m=5, largura_m=4)],  # 20 m²
        margem_perda_pct=10,
    )
    r = calcular(req, produto)

    assert r.area_liquida_m2 == 20.0
    assert r.area_com_perda_m2 == 22.0
    assert r.caixas == 11  # ceil(22 / 2.16)
    assert r.area_comprada_m2 == pytest.approx(23.76)  # 11 * 2.16
    assert r.pallets == 1
    assert r.pecas == 66  # 11 * 6
    assert r.custo_por_caixa == pytest.approx(round(2.16 * 59.90, 2))
    assert r.custo_total == pytest.approx(round(11 * round(2.16 * 59.90, 2), 2))
    assert r.sobra_m2 == pytest.approx(round(23.76 - 22.0, 4))


def test_calcular_por_area_direta():
    produto = obter_produto("essencial-bianco-60x60")
    req = CalculoRequest(produto_id=produto.id, area_m2=10.0, margem_perda_pct=0)
    r = calcular(req, produto)
    assert r.area_liquida_m2 == 10.0
    assert r.area_com_perda_m2 == 10.0
    assert r.caixas == math.ceil(10.0 / 2.16)


def test_request_exige_area_ou_comodos():
    with pytest.raises(ValueError):
        CalculoRequest(produto_id="x", margem_perda_pct=10)


def test_request_nao_aceita_ambos():
    with pytest.raises(ValueError):
        CalculoRequest(
            produto_id="x",
            area_m2=10,
            comodos=[Comodo(comprimento_m=2, largura_m=2)],
        )
