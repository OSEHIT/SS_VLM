from pydantic import BaseModel, Field
from datetime import datetime


class RLDatasetEntry(BaseModel):
    """Une entrée du dataset pour le Reinforcement Learning."""

    images_base64: list[str] = Field(..., description="Images encodées en base64")
    off_data: dict | None = Field(None, description="Données OFF brutes")
    vlm_raw: str | None = Field(None, description="Sortie brute du VLM")
    ground_truth: dict | None = Field(None, description="Vérité terrain (correction user)")
    item_count: int = Field(1, ge=1, description="Nombre d'items")
    created_at: datetime = Field(default_factory=datetime.utcnow)
