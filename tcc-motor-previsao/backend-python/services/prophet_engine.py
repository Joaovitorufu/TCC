import pandas as pd
from sqlalchemy.orm import Session
from models.hospital_record import HospitalRecord
from models.forecast_result import ForecastResult
from neuralprophet import NeuralProphet
import json

def fetch_data_for_prophet(db: Session, use_comorbidity_as_regressor=False):
    # Puxa dados agrupados por dia (contagem de internações)
    # Selecionamos apenas Dengue para simplificar a predição conforme combinado
    
    query = db.query(
        HospitalRecord.admission_date,
    ).filter(HospitalRecord.disease == "Dengue")
    
    df = pd.read_sql(query.statement, db.bind)
    if df.empty:
        return None
        
    df['admission_date'] = pd.to_datetime(df['admission_date'])
    
    if use_comorbidity_as_regressor:
        # Puxamos os dados com comorbidade para contar quantos por dia tinham comorbidade
        query_comorb = db.query(
            HospitalRecord.admission_date,
            HospitalRecord.has_comorbidity
        ).filter(HospitalRecord.disease == "Dengue")
        df_comorb = pd.read_sql(query_comorb.statement, db.bind)
        df_comorb['admission_date'] = pd.to_datetime(df_comorb['admission_date'])
        
        # Agrupa o total de internacoes por dia
        daily_counts = df_comorb.groupby('admission_date').size().reset_index(name='y')
        # Agrupa o total de comorbidades por dia (True = 1)
        daily_comorb = df_comorb.groupby('admission_date')['has_comorbidity'].sum().reset_index(name='comorb_count')
        
        df_final = pd.merge(daily_counts, daily_comorb, on='admission_date')
        df_final = df_final.rename(columns={'admission_date': 'ds'})
    else:
        # Apenas total por dia
        daily_counts = df.groupby('admission_date').size().reset_index(name='y')
        df_final = daily_counts.rename(columns={'admission_date': 'ds'})
        
    return df_final

def train_and_forecast(db: Session):
    results = []
    
    # Parametrização 1: Modelo Básico (Apenas Sazonalidade)
    print("Treinando Parametrização 1: Modelo Básico...")
    df_basic = fetch_data_for_prophet(db, use_comorbidity_as_regressor=False)
    if df_basic is not None:
        m1 = NeuralProphet(epochs=50) # Epochs reduzidas para não demorar muito no TCC local
        metrics1 = m1.fit(df_basic, freq='D')
        future1 = m1.make_future_dataframe(df_basic, periods=30)
        forecast1 = m1.predict(future1)
        
        rmse1 = metrics1['RMSE'].iloc[-1]
        mae1 = metrics1['MAE'].iloc[-1]
        
        # Formata dados
        forecast_dict1 = forecast1[['ds', 'yhat1']].tail(30).set_index('ds')['yhat1'].to_dict()
        str_dict1 = {k.strftime('%Y-%m-%d'): v for k, v in forecast_dict1.items()}
        
        res1 = ForecastResult(parameterization_name="Parametrizacao_1_Basica", rmse=float(rmse1), mae=float(mae1), forecast_data=json.dumps(str_dict1))
        db.add(res1)
        results.append(res1)

    # Parametrização 2: Modelo com Tendência Mais Flexível
    print("Treinando Parametrização 2: Alta Flexibilidade de Tendência...")
    if df_basic is not None:
        m2 = NeuralProphet(n_changepoints=100, trend_reg=0.05, epochs=50)
        metrics2 = m2.fit(df_basic, freq='D')
        future2 = m2.make_future_dataframe(df_basic, periods=30)
        forecast2 = m2.predict(future2)
        
        rmse2 = metrics2['RMSE'].iloc[-1]
        mae2 = metrics2['MAE'].iloc[-1]
        
        forecast_dict2 = forecast2[['ds', 'yhat1']].tail(30).set_index('ds')['yhat1'].to_dict()
        str_dict2 = {k.strftime('%Y-%m-%d'): v for k, v in forecast_dict2.items()}
        
        res2 = ForecastResult(parameterization_name="Parametrizacao_2_Flexivel", rmse=float(rmse2), mae=float(mae2), forecast_data=json.dumps(str_dict2))
        db.add(res2)
        results.append(res2)

    # Parametrização 3: Modelo com Comorbidade como Regressor Futuro
    print("Treinando Parametrização 3: Uso de Comorbidade como Regressor...")
    df_comorb = fetch_data_for_prophet(db, use_comorbidity_as_regressor=True)
    if df_comorb is not None:
        m3 = NeuralProphet(epochs=50)
        m3.add_future_regressor("comorb_count")
        
        metrics3 = m3.fit(df_comorb, freq='D')
        
        # Para prever com um regressor futuro, precisamos fornecer os valores dele no futuro.
        # Simulando que a média de casos com comorbidade se mantenha no futuro.
        future3 = m3.make_future_dataframe(df_comorb, periods=30)
        # Preenche os 30 dias futuros com a media móvel recente do regressor
        mean_comorb = df_comorb['comorb_count'].tail(30).mean()
        future3['comorb_count'] = mean_comorb
        
        forecast3 = m3.predict(future3)
        
        rmse3 = metrics3['RMSE'].iloc[-1]
        mae3 = metrics3['MAE'].iloc[-1]
        
        forecast_dict3 = forecast3[['ds', 'yhat1']].tail(30).set_index('ds')['yhat1'].to_dict()
        str_dict3 = {k.strftime('%Y-%m-%d'): v for k, v in forecast_dict3.items()}
        
        res3 = ForecastResult(parameterization_name="Parametrizacao_3_Comorbidade", rmse=float(rmse3), mae=float(mae3), forecast_data=json.dumps(str_dict3))
        db.add(res3)
        results.append(res3)

    db.commit()
    return results
