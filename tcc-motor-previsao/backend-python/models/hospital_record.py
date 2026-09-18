from sqlalchemy import Column, Integer, String, Date, Boolean
from database import Base

class HospitalRecord(Base):
    __tablename__ = "hospital_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    zip_code = Column(String)
    admission_date = Column(Date, index=True)
    discharge_date = Column(Date, nullable=True)
    length_of_stay = Column(Integer, nullable=True)
    disease = Column(String, index=True)
    severity = Column(String)
    has_comorbidity = Column(Boolean, default=False)
