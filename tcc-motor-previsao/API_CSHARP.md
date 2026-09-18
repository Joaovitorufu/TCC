# Documentação Técnica: API de Integração em C# (.NET 10.0)

Esta documentação detalha o funcionamento do backend em C#, responsável por atuar como uma camada intermediária (BFF - Backend for Frontend) entre o motor de Inteligência Artificial em Python e as futuras interfaces gráficas do usuário (Dashboards / Telas do Hospital).

## 1. Responsabilidade Principal
A API em C# foi construída seguindo o padrão de microsserviços. Ela não realiza processamentos matemáticos pesados de Machine Learning. O seu papel é garantir que o Front-end tenha um canal seguro, tipado e rápido para consultar as previsões de superlotação do hospital sem precisar conhecer a complexidade arquitetural do Python.

## 2. Arquitetura e Configuração
* **Framework:** Desenvolvida utilizando `.NET 10.0` com o modelo moderno e otimizado de *Minimal APIs* (centralizado no `Program.cs`).
* **Banco de Dados:** Utiliza o `Microsoft.EntityFrameworkCore.Sqlite` para se conectar diretamente ao arquivo compartilhado `hospital_forecast.db` gerado pelo Python, garantindo performance de leitura.
* **Documentação Viva:** Implementa o `Swashbuckle.AspNetCore` (Swagger) que abre automaticamente na porta `5000` (HTTP) ou `5001` (HTTPS) independente do ambiente de execução, facilitando a visualização e teste dos endpoints pela banca do TCC.

## 3. Controladores (Controllers)
O código segue o princípio de Responsabilidade Única (SRP) e foi dividido em dois controladores distintos:

### `ForecastController` (Apenas Leitura)
* **Rota:** `GET /api/Forecast`
* **Função:** Conecta-se ao SQLite e retorna a lista de previsões geradas pelo modelo (os últimos 30 dias futuros previstos, juntamente com o MAE e RMSE de cada parametrização).
* **Por que existe?** Para servir dados em tempo real para os gráficos do Front-end de forma leve e rápida, sem precisar acordar ou aguardar o motor em Python.

### `PredictionEngineController` (Orquestração / Trigger)
* **Rota:** `POST /api/PredictionEngine/run`
* **Função:** Atua como um "gatilho" para acionar o treinamento da IA.
* **Como funciona?** Utiliza a interface `IHttpClientFactory` nativa do C# para disparar uma requisição HTTP REST para o endpoint `http://127.0.0.1:8000/forecast/train` do servidor Python. Ele aguarda o término do treinamento das redes neurais e devolve a resposta (com as novas métricas) para quem o chamou.
* **Por que existe?** Para centralizar todas as chamadas. O Front-end bate apenas no C#, e o C# orquestra as comunicações externas. Se no futuro o motor Python for movido para a nuvem (AWS/Azure), bastará alterar a URL de destino dentro deste controller.
