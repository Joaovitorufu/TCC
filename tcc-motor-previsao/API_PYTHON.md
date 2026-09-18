# Documentação Técnica: Motor de Previsão em Python (IA)

Esta documentação detalha o funcionamento do backend em Python, responsável por simular o banco de dados de um hospital e executar o algoritmo de Inteligência Artificial para prever a superlotação de leitos.

## 1. Responsabilidade Principal
O motor Python atua como o "cérebro" matemático do TCC. Ele não interage diretamente com o usuário final, mas sim processa dados pesados, treina os modelos de regressão contínua usando a biblioteca **Neural Prophet** e salva os resultados matemáticos no banco de dados para serem consumidos pela API em C#.

## 2. Geração de Dados Sintéticos (RAG Simulado)
O script `scripts/generate_synthetic_data.py` é responsável por popular o banco de dados `hospital_forecast.db` (SQLite) com 15.000 registros fictícios ao longo de 5 anos.
A geração não é puramente aleatória; ela segue uma **Regra de Negócio Epidemiológica** através de um sistema de pontuação (Score de Risco) para definir a **Severidade** e o **Tempo de Internação** do paciente:

* **Comorbidades (+3 pontos):** Maior probabilidade em idosos e pacientes diagnosticados com Dengue.
* **Fator Idade (+2 pontos):** Pacientes idosos (> 65 anos) ou crianças (< 5 anos).
* **Cepa Sazonal (+2 pontos):** Pacientes diagnosticados com Dengue durante os meses de surto na cidade (Janeiro a Maio).

**Resultados do Score:**
* **Grave (Score >= 5):** Internação longa (7 a 20 dias).
* **Moderado (Score 3 ou 4):** Internação média (3 a 7 dias).
* **Leve (Score < 3):** Internação curta (1 a 3 dias).

## 3. Parametrização da Inteligência Artificial
O arquivo `services/prophet_engine.py` utiliza o Neural Prophet para avaliar os dados temporais (quantas internações por dia) e tentar adivinhar o comportamento futuro (30 dias à frente). O treinamento é dividido em 3 modelos para avaliação comparativa no TCC:

1. **Parametrização 1 (Modelo Básico):** Avalia apenas a sazonalidade bruta (altas e baixas normais ao longo do tempo).
2. **Parametrização 2 (Tendência Flexível):** Permite que a IA reaja mais rapidamente a mudanças repentinas (`n_changepoints=100`), útil para picos explosivos de Dengue.
3. **Parametrização 3 (Regressão com Comorbidade):** Utiliza a quantidade diária de pacientes com comorbidade como um "Regressor Futuro", ensinando à IA que "se houver muita comorbidade, os leitos ficarão ocupados por mais tempo".

*Nota Técnica: O parâmetro `learning_rate=0.1` foi fixado em todos os modelos para garantir compatibilidade com as políticas rigorosas de segurança introduzidas no PyTorch 2.6 (bypass no lr_find).*

## 4. Endpoints Expostos (FastAPI)
A API expõe as seguintes rotas na porta local `8000`:

* **`POST /forecast/train`**: Aciona o treinamento dos 3 modelos descritos acima. O processo lê os dados, treina as redes neurais, calcula as métricas de Erro Absoluto Médio (MAE) e Raiz do Erro Quadrático Médio (RMSE), e salva tudo no SQLite.
* **`GET /forecast/results`**: Retorna um JSON contendo os resultados matemáticos e as previsões salvas no banco de dados.
