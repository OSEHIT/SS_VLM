from pydantic import BaseModel


class OFFData(BaseModel):
    """Données extraites d'OpenFoodFacts."""

    product_name: str | None = None
    brand: str | None = None
    image_url: str | None = None
    categories: str | None = None
    nutriscore: str | None = None
    found: bool = False
