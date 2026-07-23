# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui.
O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado
- CI em três jobs: lint (ruff), testes com cobertura e build da imagem Docker.
- Workflow de release por tag semver (`vX.Y.Z`).
- Testes dos endpoints de IA (`/api/modelo/metricas` e `/api/prever-demanda`).
- Configuração do ruff, `requirements-dev.txt`, guia de contribuição e template de PR.
- Validação automática de título de PR (Conventional Commits) e Dependabot.

### Corrigido
- Encadeamento de exceção (`raise ... from exc`) no endpoint de previsão de demanda.
- Contagem de testes no README (de 27 para o valor real, 24).

## [1.0.0]

### Adicionado
- API de cálculo de material (m², caixas, pallets, peças e custo).
- Camada de IA para previsão de demanda mensal (Random Forest).
- Front-end de demonstração, Dockerfile e CI inicial.
