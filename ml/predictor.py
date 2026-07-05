"""Carrega o modelo treinado e serve previsões de demanda.

O modelo é carregado de forma preguiçosa (lazy) na primeira chamada e mantido em
cache. Se o arquivo do modelo não existir, ``prever_demanda`` levanta
``ModeloIndisponivelError`` — a API traduz isso em um HTTP 503 amigável.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd

from app.models import Produto

BASE = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE / "ml" / "model.joblib"
METRICS_PATH = BASE / "ml" / "metrics.json"


class ModeloIndisponivelError(RuntimeError):
    """Levantada quando o modelo treinado não está disponível."""


@lru_cache(maxsize=1)
def _carregar_modelo():
    if not MODEL_PATH.exists():
        raise ModeloIndisponivelError(
            "Modelo não encontrado. Rode `python -m ml.train` para treiná-lo."
        )
    return joblib.load(MODEL_PATH)


def metricas() -> Optional[dict]:
    """Retorna as métricas de avaliação do modelo, se disponíveis."""
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return None


def prever_demanda(
    produto: Produto, mes: int, indice_mercado: float, promo: bool
) -> float:
    """Prevê a demanda mensal (m²) para um produto em um dado cenário."""
    modelo = _carregar_modelo()
    entrada = pd.DataFrame(
        [
            {
                "linha": produto.linha,
                "preco_m2": produto.preco_m2,
                "mes": mes,
                "indice_mercado": indice_mercado,
                "promo": int(promo),
            }
        ]
    )
    previsao = float(modelo.predict(entrada)[0])
    return round(max(0.0, previsao), 1)
