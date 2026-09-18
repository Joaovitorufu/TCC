from fastapi import FastAPI
from routers import predict
from database import engine, Base

# Cria as tabelas ao iniciar (se não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Motor de Previsão Hospitalar - TCC",
    description="API em Python para gerar dados sintéticos e rodar o Neural Prophet",
    version="1.0.0"
)

app.include_router(predict.router)

@app.get("/")
def read_root():
    return {"message": "Motor de Previsão Hospitalar Online! Acesse /docs para o Swagger."}
