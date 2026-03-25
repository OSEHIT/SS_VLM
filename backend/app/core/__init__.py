from fastapi import HTTPException, status


class BarcodeDecodeError(Exception):
    """Impossible de décoder le code-barres depuis l'image."""


class OFFNotFoundError(Exception):
    """Produit non trouvé sur OpenFoodFacts."""


class VLMInferenceError(Exception):
    """Erreur lors de l'inférence du modèle VLM."""


class ImageProcessingError(HTTPException):
    """Erreur de traitement d'image renvoyée au client."""

    def __init__(self, detail: str = "Impossible de traiter l'image"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
