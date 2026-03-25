"""Routes CRUD /products — Gestion des produits dans MongoDB."""

from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies.mongodb import get_database
from app.schemas.product_model import ProductCreate, ProductUpdate, ProductModel

router = APIRouter(prefix="/products", tags=["Products"])


def _serialize_product(doc: dict) -> dict:
    """Convertit un document MongoDB en dict sérialisable."""
    doc["id"] = str(doc.pop("_id"))
    if "expiry_date" in doc and doc["expiry_date"]:
        # Si stocké comme string, garder tel quel
        if not isinstance(doc["expiry_date"], str):
            doc["expiry_date"] = doc["expiry_date"].isoformat()
    return doc


@router.get(
    "/",
    response_model=list[ProductModel],
    summary="Lister les produits",
    description="Récupère la liste paginée des produits depuis MongoDB.",
)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> list[ProductModel]:
    """Liste les produits."""
    cursor = db["products"].find().skip(skip).limit(limit).sort("created_at", -1)
    docs = await cursor.to_list(length=limit)
    return [ProductModel(**_serialize_product(doc)) for doc in docs]


@router.get(
    "/{product_id}",
    response_model=ProductModel,
    summary="Détail d'un produit",
)
async def get_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ProductModel:
    """Récupère un produit par son ID."""
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID produit invalide")

    doc = await db["products"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    return ProductModel(**_serialize_product(doc))


@router.post(
    "/",
    response_model=ProductModel,
    status_code=201,
    summary="Créer un produit",
    description="Crée un nouveau produit (après validation d'un scan).",
)
async def create_product(
    payload: ProductCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ProductModel:
    """Crée un produit dans MongoDB."""
    doc = payload.model_dump()
    doc["created_at"] = datetime.utcnow()

    # Convertir expiry_date en string ISO pour stockage
    if doc.get("expiry_date"):
        doc["expiry_date"] = doc["expiry_date"].isoformat()

    result = await db["products"].insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)

    return ProductModel(**doc)


@router.put(
    "/{product_id}",
    response_model=ProductModel,
    summary="Modifier un produit",
)
async def update_product(
    product_id: str,
    payload: ProductUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ProductModel:
    """Met à jour un produit existant."""
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID produit invalide")

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")

    # Convertir expiry_date en string ISO
    if "expiry_date" in update_data and update_data["expiry_date"]:
        update_data["expiry_date"] = update_data["expiry_date"].isoformat()

    await db["products"].update_one({"_id": oid}, {"$set": update_data})

    doc = await db["products"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    return ProductModel(**_serialize_product(doc))


@router.delete(
    "/{product_id}",
    summary="Supprimer un produit",
)
async def delete_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    """Supprime un produit."""
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID produit invalide")

    result = await db["products"].delete_one({"_id": oid})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    return {"status": "ok", "message": f"Produit {product_id} supprimé"}
