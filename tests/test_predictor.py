"""Testes da camada de IA (previsão de demanda) exposta pela API.

Estes testes exercitam os endpoints `/api/modelo/metricas` e
`/api/prever-demanda`, usando o modelo versionado em `ml/model.joblib`.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metricas_do_modelo():
    res = client.get("/api/modelo/metricas")
    assert res.status_code == 200
    corpo = res.json()
    # Com o modelo versionado, deve trazer as métricas de avaliação.
    assert "mae" in corpo and "r2" in corpo


def test_prever_demanda_ok():
    payload = {
        "produto_id": "urban-stone-cimento-60x60",
        "mes": 6,
        "indice_mercado": 110,
        "promo": True,
    }
    res = client.post("/api/prever-demanda", json=payload)
    assert res.status_code == 200
    corpo = res.json()
    assert corpo["demanda_prevista_m2"] >= 0
    assert corpo["mes"] == 6
    assert corpo["produto"]["id"] == "urban-stone-cimento-60x60"


def test_prever_demanda_produto_inexistente():
    payload = {"produto_id": "nao-existe", "mes": 6}
    res = client.post("/api/prever-demanda", json=payload)
    assert res.status_code == 404


def test_prever_demanda_mes_invalido():
    payload = {"produto_id": "urban-stone-cimento-60x60", "mes": 13}
    res = client.post("/api/prever-demanda", json=payload)
    assert res.status_code == 422
