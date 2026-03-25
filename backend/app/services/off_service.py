"""Service de récupération des données produit via OpenFoodFacts."""

import httpx

from app.config import get_settings
from app.schemas.product import OFFData


async def fetch_product(ean: str) -> OFFData:
    """Cherche un produit sur OpenFoodFacts par son code EAN.

    Args:
        ean: Code EAN du produit

    Returns:
        OFFData avec found=True si trouvé, found=False sinon
    """
    settings = get_settings()
    url = f"{settings.off_base_url}/product/{ean}"

    async with httpx.AsyncClient(timeout=settings.off_timeout) as client:
        try:
            response = await client.get(url, params={"fields": "product_name,brands,image_url,categories,nutriscore_grade"})
            response.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException):
            return OFFData(found=False)

    data = response.json()

    if data.get("status") != 1:
        return OFFData(found=False)

    product = data.get("product", {})
    return OFFData(
        product_name=product.get("product_name") or None,
        brand=product.get("brands") or None,
        image_url=product.get("image_url") or None,
        categories=product.get("categories") or None,
        nutriscore=product.get("nutriscore_grade") or None,
        found=True,
    )
