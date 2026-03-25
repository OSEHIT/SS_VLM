"""Schéma unifié produit — quantity est None sauf pour le vrac."""

from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field

from app.schemas.scan import ProductType


class ProductCreate(BaseModel):
    """Payload pour créer un produit depuis le mobile après validation d'un scan."""

    product_name: str | None = None
    brand: str | None = None
    expiry_date: date | None = None
    ean: str | None = None
    product_type: ProductType = ProductType.PACKAGED
    quantity: int | None = Field(None, description="Quantité (vrac uniquement)")
    source: str | None = None
    confidence: float = 0.0
    image_url: str | None = None
    image_base64: str | None = None
    display_image: str | None = Field(None, description="Image consolidée : URL OFF ou Base64 capture")
    scan_id: str | None = Field(None, description="Référence vers scan_entries")
    notification_ids: List[str] | None = Field(None, description="IDs des notifications Expo programmées")


class ProductUpdate(BaseModel):
    """Payload pour modifier un produit existant."""

    product_name: str | None = None
    brand: str | None = None
    expiry_date: date | None = None
    ean: str | None = None
    product_type: ProductType | None = None
    quantity: int | None = None
    source: str | None = None
    confidence: float | None = None
    image_url: str | None = None
    image_base64: str | None = None
    display_image: str | None = None
    notification_ids: List[str] | None = None


class ProductModel(BaseModel):
    """Schéma unifié produit (MongoDB)."""

    id: str = Field(..., description="MongoDB ObjectId")
    product_name: str | None = None
    brand: str | None = None
    expiry_date: date | None = None
    ean: str | None = None
    product_type: ProductType = ProductType.PACKAGED
    quantity: int | None = Field(None, description="Quantité (vrac uniquement)")
    source: str | None = None
    confidence: float = 0.0
    image_url: str | None = None
    image_base64: str | None = None
    display_image: str | None = Field(None, description="Image consolidée : URL OFF ou Base64 capture")
    scan_id: str | None = Field(None, description="Référence vers scan_entries")
    notification_ids: List[str] | None = Field(None, description="IDs des notifications Expo programmées")
    created_at: datetime = Field(default_factory=datetime.utcnow)
