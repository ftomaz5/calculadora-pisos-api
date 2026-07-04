# 🧮 Calculadora de Pisos — API

[![CI](https://github.com/ftomaz5/calculadora-pisos-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ftomaz5/calculadora-pisos-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

API REST que **dimensiona material de revestimento** para um ambiente: a partir das
medidas do cômodo e do produto escolhido, calcula **caixas, pallets, peças, sobra e
custo estimado** — já aplicando a margem de perda de recortes.

> Projeto de portfólio construído sobre um problema real do dia a dia da
> [FT Pisos](https://www.ftpisos.com), e-commerce de pisos e revestimentos do qual
> sou fundador. Une **domínio de negócio** e **engenharia de software**.

---

## ✨ Destaques

- **FastAPI** com documentação interativa automática (Swagger em `/docs`).
- **Regras de negócio isoladas** em funções puras — fáceis de testar e reutilizar.
- **Validação forte** com Pydantic v2 (medidas positivas, margem 0–100%, etc.).
- **Front-end de demonstração** que consome a própria API.
- **Testes automatizados** (pytest) cobrindo lógica e endpoints.
- **CI no GitHub Actions** rodando a bateria de testes a cada push.
- **Dockerfile** pronto para deploy.

---

## 🧠 Como o cálculo funciona

1. **Área líquida** = soma das áreas dos cômodos (`comprimento × largura`) ou área informada.
2. **Área com perda** = área líquida × (1 + margem%). Padrão de mercado: **10%**.
3. **Caixas** = ⌈ área com perda ÷ m² por caixa ⌉ (sempre arredonda para cima).
4. **Pallets** = ⌈ caixas ÷ caixas por pallet ⌉.
5. **Peças**, **sobra** e **custo** derivam das caixas compradas.

---

## 🚀 Como rodar

```bash
# 1. Clonar
git clone https://github.com/ftomaz5/calculadora-pisos-api.git
cd calculadora-pisos-api

# 2. Ambiente virtual + dependências
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Subir a API
uvicorn app.main:app --reload
```

Acesse:

- **Demonstração:** http://localhost:8000/
- **Documentação (Swagger):** http://localhost:8000/docs

### Com Docker

```bash
docker build -t calculadora-pisos .
docker run -p 8000:8000 calculadora-pisos
```

---

## 📡 Endpoints

| Método | Rota                     | Descrição                          |
|--------|--------------------------|------------------------------------|
| GET    | `/health`                | Verifica se a API está no ar       |
| GET    | `/api/produtos`          | Lista o catálogo de produtos       |
| GET    | `/api/produtos/{id}`     | Detalha um produto                 |
| POST   | `/api/calcular`          | Calcula o material necessário      |

### Exemplo de requisição

```bash
curl -X POST http://localhost:8000/api/calcular \
  -H "Content-Type: application/json" \
  -d '{
    "produto_id": "urban-stone-cimento-60x60",
    "comodos": [{"nome": "Sala", "comprimento_m": 5, "largura_m": 4}],
    "margem_perda_pct": 10
  }'
```

### Exemplo de resposta

```json
{
  "produto": { "id": "urban-stone-cimento-60x60", "nome": "Urban Stone Cimento", "formato": "60x60", "preco_m2": 59.9 },
  "margem_perda_pct": 10.0,
  "area_liquida_m2": 20.0,
  "area_com_perda_m2": 22.0,
  "caixas": 11,
  "area_comprada_m2": 23.76,
  "pallets": 1,
  "pecas": 66,
  "sobra_m2": 1.76,
  "custo_total": 1423.18,
  "custo_por_caixa": 129.38
}
```

---

## 🧪 Testes

```bash
pytest
```

Cobrem tanto as regras de negócio (arredondamentos, margem, validações) quanto os
endpoints da API (status codes, contratos de resposta, erros 404 e 422).

---

## 🗂️ Estrutura

```
calculadora-pisos-api/
├── app/
│   ├── main.py         # App FastAPI e rotas
│   ├── models.py       # Schemas Pydantic
│   ├── catalog.py      # Catálogo de produtos (dados)
│   └── calculator.py   # Regras de negócio (funções puras)
├── static/
│   └── index.html      # Front-end de demonstração
├── tests/
│   ├── test_calculator.py
│   └── test_api.py
├── .github/workflows/ci.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🛣️ Próximos passos (roadmap)

- Orçamento com múltiplos produtos em uma única requisição.
- Persistência em banco de dados (PostgreSQL) para o catálogo.
- Camada de dados/IA: previsão de demanda e recomendação de linha por perfil de projeto.

---

## 👤 Autor

**Flávio Tomaz** — Desenvolvedor de sistemas em formação, estudando IA · Fundador da FT Pisos
[GitHub](https://github.com/ftomaz5) · [LinkedIn](https://www.linkedin.com/in/fl%C3%A1vio-tomaz-alves-de-abreu-590116204/) · [Instagram](https://www.instagram.com/flaviotomazft)

Licença [MIT](LICENSE).
