"""Prompts dynamiques pour Qwen2-VL-2B selon le contexte du scan."""

PROMPT_EXPIRY_ONLY = """Analyze this product image carefully.
Your ONLY task is to find the expiration date (best before / use by date).

Return ONLY a JSON object:
{
  "expiry_date": "YYYY-MM-DD or null if not found",
  "confidence": 0.0 to 1.0
}

Rules:
- Look for dates labeled "DLC", "DDM", "Best Before", "Use By", "À consommer avant", "EXP"
- If MULTIPLE expiry dates are visible, return the LATEST one (furthest in the future)
- Convert any date format to YYYY-MM-DD
- If no date is visible, return null
- Do NOT invent or guess dates"""

PROMPT_FULL_EXTRACTION = """Analyze this product image carefully.
Extract ALL of the following information:

Return ONLY a JSON object:
{
  "product_name": "name of the product or null",
  "brand": "brand name or null",
  "expiry_date": "YYYY-MM-DD or null",
  "confidence": 0.0 to 1.0
}

Rules:
- Read text visible on packaging for product name and brand
- Look for dates labeled "DLC", "DDM", "Best Before", "Use By", "À consommer avant", "EXP"
- If MULTIPLE expiry dates are visible, return the LATEST one (furthest in the future)
- Convert any date format to YYYY-MM-DD
- If a field is not visible, return null
- Do NOT invent or guess information"""

PROMPT_BULK_COUNTING = """Analyze this image of bulk/fresh produce.
Your tasks:
1. Identify the type of produce (e.g., bananas, apples, tomatoes)
2. Count the number of individual items visible in the image
3. Estimate the average shelf life in days for this type of produce

Return ONLY a JSON object:
{
  "product_name": "name of the produce",
  "quantity": number of items counted,
  "shelf_life_days": estimated number of days before expiration (e.g., 5 for bananas, 14 for apples, 7 for tomatoes, 3 for strawberries),
  "confidence": 0.0 to 1.0
}

Rules:
- Count only clearly visible individual items
- If items overlap and exact count is uncertain, give your best estimate
- Set confidence lower if items are partially hidden
- For shelf_life_days, use common knowledge of produce freshness
- Do NOT estimate weight, only count items"""


def build_prompt(has_ean: bool, has_off_data: bool, is_bulk: bool = False) -> str:
    """Sélectionne le prompt VLM adapté au contexte du scan.

    Args:
        has_ean: Un code EAN a été détecté par pyzbar
        has_off_data: OpenFoodFacts a renvoyé des données
        is_bulk: L'utilisateur indique un produit en vrac
    """
    if is_bulk:
        return PROMPT_BULK_COUNTING
    if has_ean and has_off_data:
        return PROMPT_EXPIRY_ONLY
    return PROMPT_FULL_EXTRACTION
