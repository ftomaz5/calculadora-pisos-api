# Imagem enxuta com Python 3.12
FROM python:3.12-slim

WORKDIR /app

# Instala dependências primeiro (melhor cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY app ./app
COPY static ./static

EXPOSE 8000

# Sobe a API em produção
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
