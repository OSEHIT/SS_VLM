"""Route GET /export — Export du dataset RL depuis MongoDB."""

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.mongodb import get_database
from app.schemas.rl_export import RLDatasetEntry

router = APIRouter(prefix="/export", tags=["Export"])


@router.get(
    "/rl-dataset",
    response_model=list[RLDatasetEntry],
    summary="Exporter le dataset RL",
    description="Récupère les entrées de scan archivées pour l'entraînement RL.",
)
async def export_rl_dataset(
    limit: int = Query(100, ge=1, le=1000, description="Nombre max d'entrées"),
    skip: int = Query(0, ge=0, description="Nombre d'entrées à sauter"),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[RLDatasetEntry]:
    """Exporte les données de scan depuis MongoDB."""
    cursor = db["scan_entries"].find({}, {"_id": 0}).skip(skip).limit(limit).sort("created_at", -1)
    entries = await cursor.to_list(length=limit)
    return [RLDatasetEntry(**entry) for entry in entries]


@router.get(
    "/rl-dataset/count",
    summary="Nombre d'entrées RL",
    description="Retourne le nombre total d'entrées dans le dataset RL.",
)
async def count_rl_dataset(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    """Compte les entrées du dataset RL."""
    count = await db["scan_entries"].count_documents({})
    return {"count": count}
