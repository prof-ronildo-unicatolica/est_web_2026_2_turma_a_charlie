import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.busca import router as busca_router
from app.api.v1.cidades import router as cidades_router
from app.api.v1.comodidades import router as comodidades_router
from app.api.v1.health import router as health_router
from app.api.v1.interacoes import router as interacoes_router
from app.api.v1.hoteis import router as hoteis_router
from app.api.v1.quartos import router as quartos_router
from app.api.v1.sobre import router as sobre_router
from app.core.config import settings
from app.core.database import SessionLocal, get_mongo_db
from app.core.seed_admin import seed_initial_admin
from app.core.seed_mongo import seed_mongo_users
from app.models.hotel import Hotel
from app.services.catalogo_sync_service import CatalogoSyncService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_initial_admin()
    mongo_db = get_mongo_db()
    try:
        await mongo_db.command('ping')
        await seed_mongo_users(mongo_db)
        with SessionLocal() as db:
            hotel_ids = [item[0] for item in db.query(Hotel.id).all()]
            catalogo = CatalogoSyncService(db, mongo_db)
            for hotel_id in hotel_ids:
                await catalogo.sincronizar_hotel(hotel_id)
    except Exception:
        logger.exception('MongoDB indisponível: catálogo e seed não foram sincronizados.')
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

origens_permitidas = [
    origem.strip()
    for origem in settings.BACKEND_CORS_ORIGINS.split(",")
    if origem.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_permitidas,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(sobre_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(quartos_router, prefix=settings.API_V1_STR)
app.include_router(comodidades_router, prefix=settings.API_V1_STR)
app.include_router(hoteis_router, prefix=settings.API_V1_STR)
app.include_router(busca_router, prefix=settings.API_V1_STR)
app.include_router(cidades_router, prefix=settings.API_V1_STR)
app.include_router(interacoes_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Core Service do Sistema de Reservas!"}
