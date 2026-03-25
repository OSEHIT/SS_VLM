"""Orchestrateur du pipeline de scan complet.

Pipeline : Image → Barcode/QR → OFF → VLM → Fusion → ScanResponse
Si QR Code détecté avec données complètes → bypass OFF et VLM.
"""

import base64
import io
import json
from datetime import date, datetime, timedelta

from PIL import Image
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core import BarcodeDecodeError
from app.core.prompts import build_prompt
from app.dependencies.vlm import VLMContainer
from app.schemas.scan import ScanResponse, ProductType
from app.schemas.product import OFFData
from app.services.barcode_service import decode_barcode
from app.services.off_service import fetch_product
from app.services.vlm_service import run_inference


def _image_to_base64_uri(image: Image.Image) -> str:
    """Encode une image PIL en data URI Base64 JPEG."""
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=75)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


async def process_scan(
    images: list[Image.Image],
    is_bulk: bool,
    vlm: VLMContainer,
    db: AsyncIOMotorDatabase,
) -> ScanResponse:
    """Exécute le pipeline de scan complet sur une ou plusieurs images.

    Args:
        images: Liste d'images PIL envoyées par l'utilisateur
        is_bulk: True si l'utilisateur indique un produit en vrac
        vlm: Container VLM (injecté)
        db: Base MongoDB (injectée)

    Returns:
        ScanResponse avec les données fusionnées
    """
    ean: str | None = None
    off_data = OFFData(found=False)
    barcode_type: str | None = None

    # --- Étape 1 : Décodage barcode / QR Code (sur la première image) ---
    if not is_bulk:
        for img in images:
            try:
                code, barcode_type = decode_barcode(img)
                if barcode_type == "EAN":
                    ean = code
                break
            except BarcodeDecodeError:
                continue

    # --- Étape 1b : Si QR Code détecté, tenter le bypass ---
    if barcode_type == "QRCODE":
        qr_data = _parse_qr_data(code)
        if qr_data:
            # QR complet → bypass OFF et VLM
            display_img = _image_to_base64_uri(images[0])
            response = ScanResponse(
                product_name=qr_data.get("product_name"),
                brand=qr_data.get("brand"),
                expiry_date=_parse_date(qr_data.get("expiry_date")),
                quantity=None,
                ean=None,
                source="qr",
                confidence=1.0,
                product_type=ProductType.PACKAGED,
                image_url=None,
                display_image=display_img,
                raw_vlm_output=None,
            )
            scan_id = await _save_to_mongo(db, images, off_data, "", response)
            response.scan_id = scan_id
            return response

    # --- Étape 2 : Fetch OpenFoodFacts ---
    if ean:
        off_data = await fetch_product(ean)

    # --- Étape 3 : Inférence VLM ---
    prompt = build_prompt(has_ean=ean is not None, has_off_data=off_data.found, is_bulk=is_bulk)

    # Utiliser la meilleure image pour le VLM (la première)
    vlm_output = run_inference(vlm, images[0], prompt)
    raw_vlm = vlm_output.get("raw", "")

    # --- Étape 4 : Fusion des résultats ---
    response = _fuse_results(ean, off_data, vlm_output, is_bulk, images)

    # --- Étape 5 : Sauvegarde MongoDB (async, non-bloquant) ---
    scan_id = await _save_to_mongo(db, images, off_data, raw_vlm, response)
    response.scan_id = scan_id

    return response


def _parse_qr_data(qr_raw: str) -> dict | None:
    """Parse les données JSON d'un QR code.

    Retourne le dict si les champs requis sont présents, None sinon.
    """
    try:
        data = json.loads(qr_raw)
        if data.get("product_name"):
            return data
    except (json.JSONDecodeError, AttributeError):
        pass
    return None


def _fuse_results(
    ean: str | None,
    off_data: OFFData,
    vlm_output: dict,
    is_bulk: bool,
    images: list[Image.Image],
) -> ScanResponse:
    """Fusionne les données OFF et VLM en une ScanResponse unifiée."""

    confidence = vlm_output.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except (ValueError, TypeError):
        confidence = 0.0

    # Déterminer la source
    if off_data.found and ean:
        source = "off+vlm"
    elif off_data.found:
        source = "off"
    else:
        source = "vlm"

    # Extraire la date
    expiry_raw = vlm_output.get("expiry_date")
    expiry_date = _parse_date(expiry_raw)

    # Comptage pour le vrac uniquement
    quantity = None
    if is_bulk:
        try:
            quantity = int(vlm_output.get("quantity", 1))
        except (ValueError, TypeError):
            quantity = 1

    # --- Calcul DLC automatique pour le vrac ---
    if is_bulk and expiry_date is None:
        shelf_life_days = vlm_output.get("shelf_life_days")
        if shelf_life_days is not None:
            try:
                days = int(shelf_life_days)
                if 1 <= days <= 365:
                    expiry_date = date.today() + timedelta(days=days)
            except (ValueError, TypeError):
                pass

    # --- Display image : OFF URL en priorité, sinon capture Base64 ---
    display_image: str | None = None
    if off_data.image_url:
        display_image = off_data.image_url
    elif images:
        display_image = _image_to_base64_uri(images[0])

    return ScanResponse(
        product_name=off_data.product_name or vlm_output.get("product_name"),
        brand=off_data.brand or vlm_output.get("brand"),
        expiry_date=expiry_date,
        quantity=quantity,
        ean=ean,
        source=source,
        confidence=confidence,
        product_type=ProductType.BULK if is_bulk else ProductType.PACKAGED,
        image_url=off_data.image_url,
        display_image=display_image,
        raw_vlm_output=vlm_output.get("raw"),
    )


def _parse_date(raw: str | None) -> date | None:
    """Tente de parser une date depuis la sortie VLM."""
    if not raw or raw == "null":
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


async def _save_to_mongo(
    db: AsyncIOMotorDatabase,
    images: list[Image.Image],
    off_data: OFFData,
    raw_vlm: str,
    response: ScanResponse,
) -> str | None:
    """Sauvegarde l'entrée dans MongoDB pour le dataset RL.

    Returns:
        L'ObjectId inséré sous forme de string, ou None si erreur.
    """
    try:
        images_b64 = []
        for img in images:
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            images_b64.append(base64.b64encode(buffer.getvalue()).decode("utf-8"))

        entry = {
            "images_base64": images_b64,
            "off_data": off_data.model_dump() if off_data.found else None,
            "vlm_raw": raw_vlm,
            "ground_truth": None,
            "item_count": response.quantity,
            "created_at": datetime.utcnow(),
        }

        result = await db["scan_entries"].insert_one(entry)
        return str(result.inserted_id)
    except Exception as e:
        # Ne pas faire échouer le scan si MongoDB est indisponible
        print(f"[MongoDB] Erreur sauvegarde RL dataset : {e}")
        return None
