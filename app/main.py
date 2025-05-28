from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infraestructure.api.routers import generation
import logging

# Configuración básica
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    # handlers=[
    #     logging.StreamHandler(),  # Por defecto, imprime en consola
    #     logging.FileHandler('logs/backend.log')  # Guarda en archivo
    # ]
)

logger = logging.getLogger(__name__)

logger.info("Starting backend...")

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
