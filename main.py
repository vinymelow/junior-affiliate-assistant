from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(
    title="Júnior, o Parceiro | Gestor de Jornada de Leads",
    description="Assistente de IA que guia leads através de um funil de conversão multifásico via WhatsApp, pronto para ser orquestrado por N8N.",
    version="4.0.0-Stable"
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "API do Assistente Júnior (Journey Version) está online."}