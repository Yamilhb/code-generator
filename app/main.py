from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infraestructure.api.routers import generation

app = FastAPI(title="app-generator-API")

# Configuración básica de CORS para futura integración con frontend (Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes ajustar esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers específicos
app.include_router(generation.router, prefix="/api")
