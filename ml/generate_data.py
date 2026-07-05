"""Gera um dataset SINTÉTICO de demanda mensal por produto.

⚠️  Os dados são gerados artificialmente apenas para fins de demonstração do
pipeline de Machine Learning — não representam vendas reais da FT Pisos. As
relações (preço, sazonalidade, índice de mercado) foram modeladas para serem
plausíveis e permitir que o modelo aprenda padrões coerentes.

Uso:
    python -m ml.generate_data
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from app.catalog import listar_produtos

# Diretório de saída dos dados.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "vendas_sinteticas.csv"

# Semente fixa -> dataset reproduzível.
SEED = 42
N_MESES = 36  # 3 anos de histórico

# Fator sazonal por mês (1=jan ... 12=dez). Picos em reformas do meio e fim de ano.
SAZONALIDADE = {
    1: 0.80, 2: 0.85, 3: 1.05, 4: 1.10, 5: 1.00, 6: 0.90,
    7: 0.95, 8: 1.05, 9: 1.15, 10: 1.20, 11: 1.10, 12: 0.95,
}


def gerar() -> None:
    """Gera o CSV de vendas sintéticas."""
    rng = np.random.default_rng(SEED)
    produtos = listar_produtos()
    DATA_DIR.mkdir(exist_ok=True)

    linhas: list[dict] = []
    # Índice de mercado (construção civil) como passeio aleatório em torno de 100.
    indice = 100.0
    for t in range(N_MESES):
        mes = (t % 12) + 1
        indice += rng.normal(0, 3)
        indice = float(np.clip(indice, 80, 125))

        for p in produtos:
            promo = int(rng.random() < 0.15)  # ~15% dos meses em promoção
            # Demanda base cai com o preço (elasticidade) e sobe com o mercado.
            base = 900 - 4.5 * p.preco_m2
            sazonal = SAZONALIDADE[mes]
            efeito_mercado = indice / 100.0
            efeito_promo = 1.25 if promo else 1.0
            ruido = rng.normal(0, 40)

            demanda = base * sazonal * efeito_mercado * efeito_promo + ruido
            demanda = max(0.0, round(demanda, 1))

            linhas.append(
                {
                    "produto_id": p.id,
                    "linha": p.linha,
                    "preco_m2": p.preco_m2,
                    "mes": mes,
                    "indice_mercado": round(indice, 1),
                    "promo": promo,
                    "demanda_m2": demanda,
                }
            )

    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        writer.writeheader()
        writer.writerows(linhas)

    print(f"Dataset gerado: {CSV_PATH} ({len(linhas)} linhas)")


if __name__ == "__main__":
    gerar()
