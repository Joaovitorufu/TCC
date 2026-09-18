from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.forecast_result import ForecastResult
from services.prophet_engine import train_and_forecast
import json

router = APIRouter(
    prefix="/forecast",
    tags=["forecast"]
)

@router.post("/train")
def train_model(db: Session = Depends(get_db)):
    """
    Aciona o treinamento das 3 parametrizações do Neural Prophet
    (básica, flexível, comorbidade) e salva os resultados.
    """
    # Limpa previsoes anteriores (para simplificar o teste)
    db.query(ForecastResult).delete()
    db.commit()
    
    results = train_and_forecast(db)
    
    return {
        "message": "Modelos treinados com sucesso!",
        "metrics": [
            {
                "parameterization": r.parameterization_name,
                "rmse": r.rmse,
                "mae": r.mae
            } for r in results
        ]
    }

@router.get("/results")
def get_forecast_results(db: Session = Depends(get_db)):
    """
    Recupera as previsões salvas no banco de dados. 
    Este endpoint será consumido pela API em C# para o frontend.
    """
    results = db.query(ForecastResult).all()
    
    data = []
    for r in results:
        data.append({
            "id": r.id,
            "parameterization_name": r.parameterization_name,
            "rmse": r.rmse,
            "mae": r.mae,
            "forecast_data": json.loads(r.forecast_data) if r.forecast_data else {}
        })
        
    return data
