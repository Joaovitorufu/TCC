import sys
import os

# Adiciona o diretório raiz (backend-python) ao PYTHONPATH para conseguir importar models e database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta
from faker import Faker
from database import engine, Base, SessionLocal
from models.hospital_record import HospitalRecord

fake = Faker('pt_BR')

# Recria as tabelas (Atenção: vai apagar os dados antigos)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def generate_data(num_records=5000):
    db = SessionLocal()
    records = []

    # Parâmetros baseados no RAG de Uberlândia
    # A maior parte das internações nos anos de surto ocorre de janeiro a maio
    
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2025, 12, 31)
    delta = end_date - start_date

    print("Gerando dados sintéticos. Isso pode demorar um pouco...")

    for _ in range(num_records):
        # Gera uma data aleatória nesses 5 anos
        random_days = random.randrange(delta.days)
        admission = start_date + timedelta(days=random_days)
        
        # Aumentar a chance de dengue nos meses de surto (Jan a Maio)
        is_dengue_season = admission.month in [1, 2, 3, 4, 5]
        
        # 60% dos casos simulados serão Dengue durante a temporada, 20% fora da temporada
        chance_dengue = 0.6 if is_dengue_season else 0.2
        is_dengue = random.random() < chance_dengue
        disease = "Dengue" if is_dengue else random.choice(["Infeccao Respiratoria", "Problema Cardiovascular", "Trauma", "Outros"])
        
        # A idade agora influencia na gravidade (Idosos > 65 anos e crianças < 5 anos são mais vulneráveis)
        age = random.randint(0, 95)
        
        # Comorbidade afeta fortemente casos de internação por Dengue
        # Simulando que idosos e pessoas com dengue têm maior chance de ter comorbidade
        if disease == "Dengue" or age > 65:
            has_comorbidity = random.random() < 0.7
        else:
            has_comorbidity = random.random() < 0.3
            
        # Cálculo Inteligente da Severidade
        severity_score = 0
        if has_comorbidity:
            severity_score += 3
        if age > 65 or age < 5:
            severity_score += 2
        if disease == "Dengue" and is_dengue_season:
            severity_score += 2 # Cepa sazonal mais agressiva
            
        if severity_score >= 5:
            severity = "Grave"
        elif severity_score >= 3:
            severity = "Moderado"
        else:
            severity = "Leve"
            
        # O tempo de internação agora é diretamente proporcional à severidade calculada
        if severity == "Grave":
            length_of_stay = random.randint(7, 20)
        elif severity == "Moderado":
            length_of_stay = random.randint(3, 7)
        else:
            length_of_stay = random.randint(1, 3)
            
        discharge = admission + timedelta(days=length_of_stay)

        record = HospitalRecord(
            patient_name=fake.name(),
            age=age,
            gender=random.choice(["M", "F"]),
            zip_code=fake.postcode(),
            admission_date=admission.date(),
            discharge_date=discharge.date(),
            length_of_stay=length_of_stay,
            disease=disease,
            severity=severity,
            has_comorbidity=has_comorbidity
        )
        records.append(record)
        
        if len(records) >= 1000:
            db.bulk_save_objects(records)
            db.commit()
            records = []
            
    if records:
        db.bulk_save_objects(records)
        db.commit()

    db.close()
    print(f"Base de dados populada com sucesso com {num_records} registros!")

if __name__ == "__main__":
    generate_data(15000) # Gerando 15000 registros fictícios para ter volume para o modelo
