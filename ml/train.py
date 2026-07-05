"""Treina o modelo de previsão de demanda e avalia seu desempenho.

Fluxo:
    1. Carrega o dataset sintético (gera se não existir).
    2. Monta um Pipeline scikit-learn (one-hot da linha + features numéricas).
    3. Treina um RandomForestRegressor e avalia em um conjunto de teste (MAE, R²).
    4. Salva o modelo (ml/model.joblib), as métricas (ml/metrics.json) e gráficos
       de análise exploratória (docs/).

Uso:
    python -m ml.train
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")  # backend sem interface gráfica
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ml.generate_data import CSV_PATH, gerar

BASE = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE / "ml" / "model.joblib"
METRICS_PATH = BASE / "ml" / "metrics.json"
DOCS = BASE / "docs"

FEATURES_NUM = ["preco_m2", "mes", "indice_mercado", "promo"]
FEATURES_CAT = ["linha"]
TARGET = "demanda_m2"
SEED = 42


def carregar_dados() -> pd.DataFrame:
    """Carrega o CSV, gerando-o caso ainda não exista."""
    if not CSV_PATH.exists():
        gerar()
    return pd.read_csv(CSV_PATH)


def construir_pipeline() -> Pipeline:
    """Monta o pipeline de pré-processamento + modelo."""
    pre = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), FEATURES_CAT),
            ("num", "passthrough", FEATURES_NUM),
        ]
    )
    modelo = RandomForestRegressor(n_estimators=300, random_state=SEED, n_jobs=-1)
    return Pipeline([("pre", pre), ("modelo", modelo)])


def gerar_graficos(df: pd.DataFrame) -> None:
    """Gera gráficos de análise exploratória em docs/."""
    DOCS.mkdir(exist_ok=True)

    # Demanda média por mês (sazonalidade).
    por_mes = df.groupby("mes")[TARGET].mean()
    plt.figure(figsize=(8, 4))
    plt.plot(por_mes.index, por_mes.values, marker="o", color="#3b82f6")
    plt.title("Demanda média por mês (sazonalidade)")
    plt.xlabel("Mês")
    plt.ylabel("Demanda média (m²)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(DOCS / "demanda_por_mes.png", dpi=110)
    plt.close()

    # Demanda média por linha de produto.
    por_linha = df.groupby("linha")[TARGET].mean().sort_values()
    plt.figure(figsize=(8, 4))
    plt.barh(por_linha.index, por_linha.values, color="#22d3ee")
    plt.title("Demanda média por linha de produto")
    plt.xlabel("Demanda média (m²)")
    plt.tight_layout()
    plt.savefig(DOCS / "demanda_por_linha.png", dpi=110)
    plt.close()


def treinar() -> dict:
    """Treina, avalia, salva o modelo e retorna as métricas."""
    df = carregar_dados()
    X = df[FEATURES_CAT + FEATURES_NUM]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED
    )

    pipe = construir_pipeline()
    pipe.fit(X_train, y_train)

    pred = pipe.predict(X_test)
    metrics = {
        "mae": round(float(mean_absolute_error(y_test, pred)), 2),
        "r2": round(float(r2_score(y_test, pred)), 3),
        "n_amostras": int(len(df)),
        "n_treino": int(len(X_train)),
        "n_teste": int(len(X_test)),
    }

    joblib.dump(pipe, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    gerar_graficos(df)

    print("Modelo treinado e salvo em", MODEL_PATH)
    print("Métricas:", metrics)
    return metrics


if __name__ == "__main__":
    treinar()
