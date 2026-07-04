"""Catálogo de produtos da FT Pisos usado como base de dados em memória.

Em um sistema real este catálogo viria de um banco de dados. Aqui usamos um
conjunto curado e realista das linhas da FT Pisos para manter o projeto simples,
determinístico e fácil de testar.
"""

from __future__ import annotations

from typing import Dict, List

from .models import Produto

# Valores realistas de porcelanato/cerâmica (m² por caixa, peças, etc.).
_PRODUTOS: List[Produto] = [
    Produto(
        id="marmore-carrara-80x80",
        nome="Mármore Carrara Polido",
        linha="Mármore",
        formato="80x80",
        m2_por_caixa=1.92,
        pecas_por_caixa=3,
        caixas_por_pallet=40,
        preco_m2=89.90,
    ),
    Produto(
        id="madeira-nature-20x120",
        nome="Madeira Nature",
        linha="Madeira",
        formato="20x120",
        m2_por_caixa=2.16,
        pecas_por_caixa=9,
        caixas_por_pallet=48,
        preco_m2=74.50,
    ),
    Produto(
        id="urban-stone-cimento-60x60",
        nome="Urban Stone Cimento",
        linha="Urban Stone",
        formato="60x60",
        m2_por_caixa=2.16,
        pecas_por_caixa=6,
        caixas_por_pallet=48,
        preco_m2=59.90,
    ),
    Produto(
        id="essencial-bianco-60x60",
        nome="Essencial Bianco",
        linha="Essencial",
        formato="60x60",
        m2_por_caixa=2.16,
        pecas_por_caixa=6,
        caixas_por_pallet=56,
        preco_m2=42.90,
    ),
    Produto(
        id="decorada-rochaprime-60x120",
        nome="Decorada RochaPrime",
        linha="Decorada",
        formato="60x120",
        m2_por_caixa=1.44,
        pecas_por_caixa=2,
        caixas_por_pallet=32,
        preco_m2=119.90,
    ),
]

# Índice por id para acesso O(1).
_INDICE: Dict[str, Produto] = {p.id: p for p in _PRODUTOS}


def listar_produtos() -> List[Produto]:
    """Retorna todos os produtos do catálogo."""
    return list(_PRODUTOS)


def obter_produto(produto_id: str) -> Produto | None:
    """Retorna um produto pelo id, ou ``None`` se não existir."""
    return _INDICE.get(produto_id)
