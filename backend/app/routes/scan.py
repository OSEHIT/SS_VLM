"""Route POST /scan — Point d'entrée principal du pipeline."""

from fastapi import APIRouter, Depends, File, Query, UploadFile
from PIL import Image
import io

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.vlm import VLMContainer, get_vlm
from app.dependencies.mongodb import get_database
from app.schemas.scan import ScanResponse
from app.core import ImageProcessingError
from app.services.scan_orchestrator import process_scan

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.post(
    "",
    response_model=ScanResponse,
    summary="Scanner un produit",
    description=(
        "Envoie une ou plusieurs images (code-barres, emballage, produit brut) "
        "pour identification via le pipeline barcode → OFF → VLM."
    ),
)
async def scan_product(
    images: list[UploadFile] = File(..., description="Images du produit"),
    is_bulk: bool = Query(False, description="True si produit en vrac (fruits/légumes)"),
    vlm: VLMContainer = Depends(get_vlm),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ScanResponse:
    """Traite les images envoyées et retourne les informations produit."""
    if not images:
        raise ImageProcessingError("Aucune image reçue")

    pil_images: list[Image.Image] = []
    for upload in images:
        try:
            content = await upload.read()
            img = Image.open(io.BytesIO(content)).convert("RGB")
            pil_images.append(img)
        except Exception:
            raise ImageProcessingError(f"Image invalide : {upload.filename}")

    return await process_scan(
        images=pil_images,
        is_bulk=is_bulk,
        vlm=vlm,
        db=db,
    )
