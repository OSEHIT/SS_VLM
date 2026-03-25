"""Schéma pour le feedback Reinforcement Learning."""

from pydantic import BaseModel, Field


class RLFeedbackRequest(BaseModel):
    """Requête de feedback RL envoyée par le mobile."""

    scan_id: str = Field(..., description="MongoDB ObjectId de l'entrée scan originale")
    ground_truth: dict = Field(..., description="Données corrigées/validées par l'utilisateur")
