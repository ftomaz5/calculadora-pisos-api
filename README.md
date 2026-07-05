# 🧮 Calculadora de Pisos — API

[![CI](https://github.com/ftomaz5/calculadora-pisos-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ftomaz5/calculadora-pisos-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)
![Tests](https://img.shields.io/badge/tests-27%20passing-3fb950?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

API REST que **dimensiona material de revestimento** e **prevê a demanda mensal** de
produtos. A partir das medidas de um ambiente, calcula **caixas, pallets, peças, sobra e
custo**; e, com um modelo de **Machine Learning**, estima a **demanda (m²/mês)** de cada
produto conforme mês, preço, índice de mercado e promoção.

> Projeto de portfólio construído sobre um problema real do dia a dia da
> [FT Pisos](https://www.ftpisos.com), e-commerce de pisos do qual sou fundador.
> Une **domínio de negócio**, **engenharia de software** e **ciência de dados**.

---

## ✨ Destaques

- **FastAPI** com documentação interativa automática (Swagger em `/docs`).
- **Regras de negócio isoladas** em funções puras — fáceis de testar e reutilizar.
- **Camada de IA** de ponta a ponta: geração de dados → treino → avaliação → serviço.
- **Validação forte** com Pydantic v2.
- **Front-end de demonstração** que consome a própria API.
- **27 testes automatizados** (pytest) cobrindo lógica, endpoints e o modelo.
- **CI no GitHub Actions** e **Dockerfile** prontos.

---

## 🧠 Como o cálculo funciona

1. **Área líquida** = soma das áreas dos cômodos (`comprimento × largura`) ou área informada.
2. **Área com perda** = área líquida × (1 + margem%). Padrão de mercado: **10%**.
3. **Caixas** = ⌈ área com perda ÷ m² por caixa ⌉ (arredonda para cima).
4. **Pallets**, **peças**, **sobra** e **custo** derivam das caixas compradas.

---

## 🤖 Camada de IA — Previsão de demanda

Um modelo de **regressão (Random Forest, scikit-learn)** estima a demanda mensal de cada
produto a partir de: **linha**, **preço/m²**, **mês** (sazonalidade), **índice de mercado**
e **promoção**.

> ⚠️ **Dados sintéticos:** o dataset é gerado artificialmente (`ml/generate_data.py`)
> apenas para demonstrar o pipeline de ML — não são vendas reais. As relações foram
> modeladas para serem plausíveis (elasticidade de preço, sazonalidade, efeito de promoção).

**Pipeline:** `OneHotEncoder` (linha) + features numéricas → `RandomForestRegressor`,
avaliado em conjunto de teste separado.

**Desempenho do modelo:**

| Métrica | Valor |
|---------|-------|
| R²      | **0.888** |
| MAE     | **42.83 m²** |
| Amostras (treino / teste) | 144 / 36 |

**Análise exploratória (gerada automaticamente):**

![Demanda média por mês](docs/demanda_por_mes.png)
![Demanda média por linha](docs/demanda_por_linha.png)

Para regenerar dados, treinar e produzir os gráficos:

```bash
python -m ml.generate_data   # cria data/vendas_sinteticas.csv
python -m ml.train           # treina, avalia, salva ml/model.joblib e docs/*.png
```

---

## 🚀 Como rodar

```bash
git clone https://github.com/ftomaz5/calculadora-pisos-api.git
cd calculadora-pisos-api

python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Acesse **http://localhost:8000/** (demonstração) e **http://localhost:8000/docs** (Swagger).

### Com Docker

```bash
docker build -t calculadora-pisos .
docker run -p 8000:8000 calculadora-pisos
```

---

## 📡 Endpoints

| Método | Rota                     | Descrição                              |
|--------|--------------------------|----------------------------------------|
| GET    | `/health`                | Verifica se a API está no ar           |
| GET    | `/api/produtos`          | Lista o catálogo de produtos           |
| GET    | `/api/produtos/{id}`     | Detalha um produto                     |
| POST   | `/api/calcular`          | Calcula o material necessário          |
| POST   | `/api/prever-demanda`    | **Prevê a demanda mensal (IA)**        |
| GET    | `/api/modelo/metricas`   | **Métricas do modelo (IA)**            |

### Exemplo — cálculo de material

```bash
curl -X POST http://localhost:8000/api/calcular \
  -H "Content-Type: application/json" \
  -d '{"produto_id":"urban-stone-cimento-60x60","comodos":[{"comprimento_m":5,"largura_m":4}],"margem_perda_pct":10}'
```

### Exemplo — previsão de demanda (IA)

```bash
curl -X POST http://localhost:8000/api/prever-demanda \
  -H "Content-Type: application/json" \
  -d '{"produto_id":"essencial-bianco-60x60","mes":10,"indice_mercado":115,"promo":true}'
```

```json
{
  "produto": { "id": "essencial-bianco-60x60", "linha": "Essencial", "preco_m2": 42.9 },
  "mes": 10,
  "indice_mercado": 115.0,
  "promo": true,
  "demanda_prevista_m2": 1041.5,
  "unidade": "m²/mês"
}
```

---

## 🧪 Testes

```bash
pytest
```

27 testes cobrindo as regras de negócio, os endpoints e o modelo de IA.

---

## 🗂️ Estrutura

```
calculadora-pisos-api/
├── app/                # API FastAPI
│   ├── main.py         # Rotas (cálculo + IA)
│   ├── models.py       # Schemas Pydantic
│   ├── catalog.py      # Catálogo de produtos
│   └── calculator.py   # Regras de negócio (funções puras)
├── ml/                 # Camada de dados / Machine Learning
│   ├── generate_data.py  # Geração do dataset sintético
│   ├── train.py          # Treino, avaliação e gráficos
│   ├── predictor.py      # Carrega o modelo e prevê
│   ├── model.joblib      # Modelo treinado (artefato)
│   └── metrics.json      # Métricas de avaliação
├── data/               # Dataset sintético (CSV)
├── docs/               # Gráficos de análise exploratória
├── static/index.html   # Front-end de demonstração
├── tests/              # Testes (lógica, API e IA)
├── .github/workflows/ci.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🛣️ Roadmap

- [x] API de cálculo de material
- [x] Camada de IA: previsão de demanda
- [ ] Orçamento com múltiplos produtos numa requisição
- [ ] Persistência do catálogo em banco de dados (PostgreSQL)
- [ ] Recomendação de linha por perfil de projeto

---

## 👤 Autor

**Flávio Tomaz** — Desenvolvedor de sistemas em formação, estudando IA · Fundador da FT Pisos
[GitHub](https://github.com/ftomaz5) · [LinkedIn](https://www.linkedin.com/in/fl%C3%A1vio-tomaz-alves-de-abreu-590116204/) · [Instagram](https://www.instagram.com/flaviotomazft)

Licença [MIT](LICENSE).
