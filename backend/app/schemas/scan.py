from pydantic import BaseModel, Field
from datetime import date
from enum import Enum


class ProductType(str, Enum):
    PACKAGED = "packaged"
    BULK = "bulk"


class ScanResponse(BaseModel):
    """Réponse unifiée après le pipeline scan."""

    scan_id: str | None = Field(None, description="ID MongoDB de l'entrée scan (pour RL feedback)")
    product_name: str | None = Field(None, description="Nom du produit")
    brand: str | None = Field(None, description="Marque")
    expiry_date: date | None = Field(None, description="Date de péremption (DLC)")
    quantity: int | None = Field(None, description="Quantité détectée (vrac uniquement)")
    ean: str | None = Field(None, description="Code EAN si détecté")
    source: str = Field(..., description="Source des données : 'off', 'vlm', 'off+vlm', 'qr'")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Score de confiance VLM")
    product_type: ProductType = Field(ProductType.PACKAGED)
    image_url: str | None = Field(None, description="URL image OFF si disponible")
    display_image: str | None = Field(None, description="Image consolidée : URL OFF ou Base64 de la capture")
    raw_vlm_output: str | None = Field(None, description="Sortie brute VLM (pour dataset RL)")
