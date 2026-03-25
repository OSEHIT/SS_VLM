"""Dependency injection pour MongoDB (dataset RL)."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

_client: AsyncIOMotorClient | None = None


async def connect_mongo() -> None:
    """Initialise la connexion MongoDB (appelé dans le lifespan)."""
    global _client
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    print(f"[MongoDB] Connecté à {settings.mongodb_uri}")


async def close_mongo() -> None:
    """Ferme la connexion MongoDB."""
    global _client
    if _client:
        _client.close()
        _client = None
        print("[MongoDB] Connexion fermée.")


def get_database() -> AsyncIOMotorDatabase:
    """Dependency FastAPI pour injecter la base MongoDB."""
    if _client is None:
        raise RuntimeError("MongoDB non connecté. Vérifiez le lifespan de l'app.")
    settings = get_settings()
    return _client[settings.mongodb_db_name]
