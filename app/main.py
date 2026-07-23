"""Aplicação FastAPI da Calculadora de Pisos.

Expõe o catálogo de produtos e o endpoint de cálculo de material, além de servir
uma página de demonstração e a documentação interativa (Swagger UI em ``/docs``).
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .calculator import calcular
from .catalog import listar_produtos, obter_produto
from .models import CalculoRequest, CalculoResponse, ErrorResponse, Produto

app = FastAPI(
    title="Calculadora de Pisos API",
    description=(
        "API para dimensionamento de revestimentos: calcula m², caixas, pallets, "
        "peças e custo estimado a partir das dimensões de um ambiente. "
        "Projeto de portfólio inspirado no domínio real da FT Pisos."
    ),
    version=__version__,
    contact={"name": "Flávio Tomaz", "url": "https://github.com/ftomaz5"},
    license_info={"name": "MIT"},
)

# Libera o consumo por front-ends (ex.: a página de demonstração).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/health", tags=["infra"], summary="Verifica se a API está no ar")
def health() -> dict:
    """Endpoint simples de verificação de saúde."""
    return {"status": "ok", "versao": __version__}


@app.get(
    "/api/produtos",
    response_model=List[Produto],
    tags=["catálogo"],
    summary="Lista todos os produtos",
)
def get_produtos() -> List[Produto]:
    """Retorna o catálogo completo de produtos disponíveis."""
    return listar_produtos()


@app.get(
    "/api/produtos/{produto_id}",
    response_model=Produto,
    tags=["catálogo"],
    summary="Detalha um produto",
    responses={404: {"model": ErrorResponse}},
)
def get_produto(produto_id: str) -> Produto:
    """Retorna um produto específico pelo id."""
    produto = obter_produto(produto_id)
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto '{produto_id}' não encontrado.",
        )
    return produto


@app.post(
    "/api/calcular",
    response_model=CalculoResponse,
    tags=["cálculo"],
    summary="Calcula o material necessário",
    responses={404: {"model": ErrorResponse}},
)
def post_calcular(request: CalculoRequest) -> CalculoResponse:
    """Calcula caixas, pallets, peças e custo para revestir uma área."""
    produto = obter_produto(request.produto_id)
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto '{request.produto_id}' não encontrado.",
        )
    return calcular(request, produto)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    """Serve a página de demonstração."""
    return FileResponse(_STATIC_DIR / "index.html")


# Arquivos estáticos (CSS/JS/imagens) da demonstração.
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


# ---------------------------------------------------------------------------
# Camada de IA: previsão de demanda (modelo de Machine Learning)
# ---------------------------------------------------------------------------
from app.models import PrevisaoRequest, PrevisaoResponse  # noqa: E402
from ml.predictor import (  # noqa: E402
    ModeloIndisponivelError,
    metricas,
    prever_demanda,
)


@app.get(
    "/api/modelo/metricas",
    tags=["ia"],
    summary="Métricas de avaliação do modelo",
)
def get_metricas() -> dict:
    """Retorna as métricas (MAE, R²) do modelo de previsão, se disponíveis."""
    m = metricas()
    if m is None:
        return {"detail": "Modelo ainda não treinado."}
    return m


@app.post(
    "/api/prever-demanda",
    response_model=PrevisaoResponse,
    tags=["ia"],
    summary="Prevê a demanda mensal de um produto",
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def post_prever_demanda(request: PrevisaoRequest) -> PrevisaoResponse:
    """Prevê a demanda mensal (m²) para um produto usando o modelo de ML."""
    produto = obter_produto(request.produto_id)
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto '{request.produto_id}' não encontrado.",
        )
    try:
        demanda = prever_demanda(
            produto=produto,
            mes=request.mes,
            indice_mercado=request.indice_mercado,
            promo=request.promo,
        )
    except ModeloIndisponivelError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    return PrevisaoResponse(
        produto=produto,
        mes=request.mes,
        indice_mercado=request.indice_mercado,
        promo=request.promo,
        demanda_prevista_m2=demanda,
    )
