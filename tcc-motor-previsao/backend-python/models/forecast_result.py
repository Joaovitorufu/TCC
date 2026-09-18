from sqlalchemy import Column, Integer, String, Float, JSON
from database import Base

class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id = Column(Integer, primary_key=True, index=True)
    parameterization_name = Column(String, index=True)
    rmse = Column(Float)
    mae = Column(Float)
    forecast_data = Column(JSON) # Pode armazenar um dicionário json com as previsões (data: valor)
