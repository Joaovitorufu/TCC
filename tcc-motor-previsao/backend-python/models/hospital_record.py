from sqlalchemy import Column, Integer, String, Date, Boolean
from database import Base

class HospitalRecord(Base):
    __tablename__ = "registros_hospitalares"

    id = Column(Integer, primary_key=True, index=True)
    nome_paciente = Column(String, index=True)
    idade = Column(Integer)
    sexo = Column(String)
    data_internacao = Column(Date, index=True)
    data_alta = Column(Date, nullable=True)
    tempo_internacao = Column(Integer, nullable=True)
    doenca = Column(String, index=True)
    severidade = Column(String)
    possui_comorbidade = Column(Boolean, default=False)
