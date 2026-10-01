import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from models.hospital_record import HospitalRecord
from models.forecast_result import ForecastResult
from neuralprophet import NeuralProphet
import json

def fetch_data_for_prophet(db: Session, use_comorbidity_as_regressor=False):
    # Puxa dados agrupados por dia (contagem de internações)
    # Selecionamos apenas Dengue para a predição
    query = db.query(
        HospitalRecord.data_internacao,
    ).filter(HospitalRecord.doenca == "Dengue")
    
    df = pd.read_sql(query.statement, db.bind)
    if df.empty:
        return None
        
    df['data_internacao'] = pd.to_datetime(df['data_internacao'])
    
    # 1. Pré-processamento: Criação do calendário contínuo (sem lacunas)
    data_inicio = df['data_internacao'].min()
    data_fim = df['data_internacao'].max()
    calendario_completo = pd.date_range(start=data_inicio, end=data_fim, freq='D')
    
    if use_comorbidity_as_regressor:
        # Puxamos dados com indicador de comorbidade
        query_comorb = db.query(
            HospitalRecord.data_internacao,
            HospitalRecord.possui_comorbidade
        ).filter(HospitalRecord.doenca == "Dengue")
        df_comorb = pd.read_sql(query_comorb.statement, db.bind)
        df_comorb['data_internacao'] = pd.to_datetime(df_comorb['data_internacao'])
        
        # Agrupa contagem de internações por dia e preenche dias vazios com zero
        daily_counts = df_comorb.groupby('data_internacao').size().reindex(calendario_completo, fill_value=0).reset_index()
        daily_counts.columns = ['ds', 'y']
        
        # Agrupa contagem de comorbidades por dia e preenche dias vazios com zero
        daily_comorb = df_comorb.groupby('data_internacao')['possui_comorbidade'].sum().reindex(calendario_completo, fill_value=0).reset_index()
        daily_comorb.columns = ['ds', 'comorb_count']
        
        df_final = pd.merge(daily_counts, daily_comorb, on='ds')
    else:
        # Contagem diária com preenchimento de zero para dias sem internação
        daily_counts = df.groupby('data_internacao').size().reindex(calendario_completo, fill_value=0).reset_index()
        daily_counts.columns = ['ds', 'y']
        df_final = daily_counts
        
    # Garante ordenação cronológica estrita
    df_final = df_final.sort_values('ds').reset_index(drop=True)
    return df_final

def train_and_forecast(db: Session):
    results = []
    
    # =========================================================================
    # Parametrização 1: Modelo Básico (Apenas Sazonalidade)
    # =========================================================================
    print("Treinando Parametrização 1: Modelo Básico (com avaliação em dados inéditos)...")
    df_basic = fetch_data_for_prophet(db, use_comorbidity_as_regressor=False)
    if df_basic is not None and len(df_basic) > 30:
        # Divisão Temporal: Treino (até -30 dias) vs Teste (últimos 30 dias inéditos)
        df_train1 = df_basic.iloc[:-30].copy()
        df_test1 = df_basic.iloc[-30:].copy()
        
        m1 = NeuralProphet(epochs=50, learning_rate=0.1)
        m1.fit(df_train1, freq='D')
        
        future1 = m1.make_future_dataframe(df_train1, periods=30)
        forecast1 = m1.predict(future1)
        
        # Cálculo de erro REAL sobre os 30 dias inéditos
        y_real1 = df_test1['y'].values
        y_pred1 = forecast1['yhat1'].tail(30).values
        
        rmse1 = float(np.sqrt(np.mean((y_real1 - y_pred1) ** 2)))
        mae1 = float(np.mean(np.abs(y_real1 - y_pred1)))
        
        # Formata dados previstos e reais para salvar
        str_dict1 = {}
        dates_test = df_test1['ds'].dt.strftime('%Y-%m-%d').values
        for d_str, y_p, y_r in zip(dates_test, y_pred1, y_real1):
            str_dict1[d_str] = {"predicted": round(float(y_p), 2), "actual": float(y_r)}
        
        res1 = ForecastResult(
            parameterization_name="Parametrizacao_1_Basica", 
            rmse=round(rmse1, 4), 
            mae=round(mae1, 4), 
            forecast_data=json.dumps(str_dict1)
        )
        db.add(res1)
        results.append(res1)

    # =========================================================================
    # Parametrização 2: Modelo com Tendência Mais Flexível
    # =========================================================================
    print("Treinando Parametrização 2: Alta Flexibilidade (com avaliação em dados inéditos)...")
    if df_basic is not None and len(df_basic) > 30:
        df_train2 = df_basic.iloc[:-30].copy()
        df_test2 = df_basic.iloc[-30:].copy()
        
        m2 = NeuralProphet(n_changepoints=100, trend_reg=0.05, epochs=50, learning_rate=0.1)
        m2.fit(df_train2, freq='D')
        
        future2 = m2.make_future_dataframe(df_train2, periods=30)
        forecast2 = m2.predict(future2)
        
        y_real2 = df_test2['y'].values
        y_pred2 = forecast2['yhat1'].tail(30).values
        
        rmse2 = float(np.sqrt(np.mean((y_real2 - y_pred2) ** 2)))
        mae2 = float(np.mean(np.abs(y_real2 - y_pred2)))
        
        str_dict2 = {}
        dates_test = df_test2['ds'].dt.strftime('%Y-%m-%d').values
        for d_str, y_p, y_r in zip(dates_test, y_pred2, y_real2):
            str_dict2[d_str] = {"predicted": round(float(y_p), 2), "actual": float(y_r)}
        
        res2 = ForecastResult(
            parameterization_name="Parametrizacao_2_Flexivel", 
            rmse=round(rmse2, 4), 
            mae=round(mae2, 4), 
            forecast_data=json.dumps(str_dict2)
        )
        db.add(res2)
        results.append(res2)

    # =========================================================================
    # Parametrização 3: Modelo com Comorbidade como Regressor Futuro
    # =========================================================================
    print("Treinando Parametrização 3: Uso de Comorbidade (com avaliação em dados inéditos)...")
    df_comorb = fetch_data_for_prophet(db, use_comorbidity_as_regressor=True)
    if df_comorb is not None and len(df_comorb) > 30:
        df_train3 = df_comorb.iloc[:-30].copy()
        df_test3 = df_comorb.iloc[-30:].copy()
        
        m3 = NeuralProphet(epochs=50, learning_rate=0.1)
        m3.add_future_regressor("comorb_count")
        m3.fit(df_train3, freq='D')
        
        # Para testar os 30 dias inéditos, fornecemos o regressor real que ocorreu nesse mês de teste
        regressors_test = df_test3[['ds', 'comorb_count']]
        future3 = m3.make_future_dataframe(df_train3, regressors_df=regressors_test, periods=30)
        forecast3 = m3.predict(future3)
        
        y_real3 = df_test3['y'].values
        y_pred3 = forecast3['yhat1'].tail(30).values
        
        rmse3 = float(np.sqrt(np.mean((y_real3 - y_pred3) ** 2)))
        mae3 = float(np.mean(np.abs(y_real3 - y_pred3)))
        
        str_dict3 = {}
        dates_test = df_test3['ds'].dt.strftime('%Y-%m-%d').values
        for d_str, y_p, y_r in zip(dates_test, y_pred3, y_real3):
            str_dict3[d_str] = {"predicted": round(float(y_p), 2), "actual": float(y_r)}
        
        res3 = ForecastResult(
            parameterization_name="Parametrizacao_3_Comorbidade", 
            rmse=round(rmse3, 4), 
            mae=round(mae3, 4), 
            forecast_data=json.dumps(str_dict3)
        )
        db.add(res3)
        results.append(res3)

    db.commit()
    return results
