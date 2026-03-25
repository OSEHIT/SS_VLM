"""FastAPI App Factory — Smart Shelf V2.

Lifespan gère le chargement du VLM et la connexion MongoDB.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.dependencies.vlm import vlm_container
from app.dependencies.mongodb import connect_mongo, close_mongo
from app.routes import scan, export, rl_feedback, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan : charge le VLM et connecte MongoDB au démarrage."""
    settings = get_settings()

    # Startup
    print("=" * 50)
    print("🚀 Smart Shelf V2 — Démarrage")
    print("=" * 50)

    vlm_container.load()
    await connect_mongo()

    print(f"📡 API prête sur http://{settings.host}:{settings.port}")
    print(f"📖 Swagger UI : http://{settings.host}:{settings.port}/docs")
    print("=" * 50)

    yield

    # Shutdown
    vlm_container.unload()
    await close_mongo()
    print("👋 Smart Shelf V2 — Arrêt propre")


def create_app() -> FastAPI:
    """Factory pour créer l'application FastAPI."""
    settings = get_settings()

    app = FastAPI(
        title="Smart Shelf V2 API",
        description=(
            "API de scan de produits alimentaires avec reconnaissance visuelle (VLM), "
            "décodage barcode/QR, et intégration OpenFoodFacts."
        ),
        version="2.0.0",
        lifespan=lifespan,
    )

    # CORS — localhost pour Expo en dev
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(scan.router, prefix="/api/v1")
    app.include_router(export.router, prefix="/api/v1")
    app.include_router(rl_feedback.router, prefix="/api/v1")
    app.include_router(products.router, prefix="/api/v1")

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "ok",
            "vlm_loaded": vlm_container.is_loaded,
            "version": "2.0.0",
        }

    return app


app = create_app()
