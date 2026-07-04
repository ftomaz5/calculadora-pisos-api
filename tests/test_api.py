"""Testes dos endpoints da API usando o TestClient do FastAPI."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_listar_produtos():
    res = client.get("/api/produtos")
    assert res.status_code == 200
    produtos = res.json()
    assert len(produtos) >= 1
    assert {"id", "nome", "preco_m2", "m2_por_caixa"} <= set(produtos[0].keys())


def test_obter_produto_existente():
    res = client.get("/api/produtos/madeira-nature-20x120")
    assert res.status_code == 200
    assert res.json()["linha"] == "Madeira"


def test_obter_produto_inexistente():
    res = client.get("/api/produtos/nao-existe")
    assert res.status_code == 404


def test_calcular_ok():
    payload = {
        "produto_id": "urban-stone-cimento-60x60",
        "comodos": [{"comprimento_m": 5, "largura_m": 4}],
        "margem_perda_pct": 10,
    }
    res = client.post("/api/calcular", json=payload)
    assert res.status_code == 200
    d = res.json()
    assert d["caixas"] == 11
    assert d["pallets"] == 1
    assert d["custo_total"] > 0


def test_calcular_produto_invalido():
    payload = {"produto_id": "xxx", "area_m2": 10}
    res = client.post("/api/calcular", json=payload)
    assert res.status_code == 404


def test_calcular_sem_area_da_erro_422():
    res = client.post("/api/calcular", json={"produto_id": "essencial-bianco-60x60"})
    assert res.status_code == 422


def test_calcular_margem_fora_do_limite():
    payload = {"produto_id": "essencial-bianco-60x60", "area_m2": 10, "margem_perda_pct": 150}
    res = client.post("/api/calcular", json=payload)
    assert res.status_code == 422
