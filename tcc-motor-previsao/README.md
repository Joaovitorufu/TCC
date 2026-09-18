# Motor de Previsão Hospitalar - TCC

Este repositório contém o código-fonte desenvolvido para o Trabalho de Conclusão de Curso (TCC).
O sistema é um Motor de Previsão baseado no Neural Prophet focado em prever a superlotação de um único hospital, parametrizado com base nos dados do **Relatório Anual de Gestão 2025 de Uberlândia**.

## Estrutura do Projeto

O projeto é dividido em dois microserviços:

### 1. `backend-python/` (Motor de Previsão e Banco de Dados)
Responsável por gerar os dados sintéticos, treinar as parametrizações do Neural Prophet e armazenar os resultados.

**Para rodar:**
1. Navegue até a pasta: `cd backend-python`
2. Instale as dependências: `pip install -r requirements.txt`
3. Gere a base de dados sintética com a flag de comorbidade (5 anos de histórico): `python scripts/generate_synthetic_data.py`
4. Rode a API do FastAPI: `uvicorn main:app --reload`
5. Acesse a documentação interativa e os endpoints em: `http://127.0.0.1:8000/docs`

### 2. `backend-csharp/` (API de Consumo para o Front-end)
Responsável por conectar no banco gerado pelo Python e expor os dados das previsões para o futuro Front-end do hospital. Também possui um endpoint para acionar o treinamento dos modelos no motor Python.

**Endpoints Principais:**
- `GET /api/Forecast`: Retorna os resultados das previsões salvas no banco.
- `POST /api/PredictionEngine/run`: Chama a API em Python (na porta 8000) para iniciar o treinamento do modelo e gerar novas previsões.

**Para rodar:**
1. Navegue até a pasta: `cd backend-csharp`
2. Restaure os pacotes: `dotnet restore`
3. Rode a API: `dotnet run`
4. Acesse a documentação no Swagger no navegador (a porta aparecerá no console).

> **Atenção:** Para que o endpoint de treinamento (`/api/PredictionEngine/run`) funcione, a API do `backend-python` deve estar em execução simultaneamente na porta `8000`.
