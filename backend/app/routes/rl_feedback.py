"""Route POST /rl-feedback — Feedback Reinforcement Learning."""

from fastapi import APIRouter, Depends
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.mongodb import get_database
from app.schemas.rl_feedback import RLFeedbackRequest

router = APIRouter(prefix="/rl-feedback", tags=["RL Feedback"])


@router.post(
    "",
    summary="Soumettre un feedback RL",
    description=(
        "Met à jour l'entrée scan correspondante dans MongoDB avec les données "
        "corrigées/validées par l'utilisateur (ground_truth)."
    ),
)
async def submit_rl_feedback(
    payload: RLFeedbackRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    """Enregistre le feedback RL dans la collection scan_entries."""
    try:
        object_id = ObjectId(payload.scan_id)
    except Exception:
        return {"status": "error", "message": "scan_id invalide"}

    result = await db["scan_entries"].update_one(
        {"_id": object_id},
        {"$set": {"ground_truth": payload.ground_truth}},
    )

    if result.matched_count == 0:
        return {"status": "error", "message": "Entrée scan non trouvée"}

    return {"status": "ok", "message": "Feedback RL enregistré", "scan_id": payload.scan_id}
