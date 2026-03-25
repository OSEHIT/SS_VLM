"""Tests pour le scan_orchestrator — fusion et DLC auto."""

from datetime import date, timedelta

from PIL import Image

from app.schemas.product import OFFData
from app.schemas.scan import ProductType
from app.services.scan_orchestrator import _fuse_results, _image_to_base64_uri


def _make_image(w: int = 10, h: int = 10) -> Image.Image:
    return Image.new("RGB", (w, h), color="blue")


class TestFuseResultsBulkDLC:
    """Vérifie le calcul automatique de la DLC pour le vrac."""

    def test_bulk_dlc_with_shelf_life_days(self):
        """shelf_life_days=5 → expiry_date = today + 5."""
        vlm = {"product_name": "Bananes", "quantity": 3, "shelf_life_days": 5, "confidence": 0.9}
        off = OFFData(found=False)
        images = [_make_image()]

        result = _fuse_results(None, off, vlm, is_bulk=True, images=images)

        assert result.product_type == ProductType.BULK
        assert result.expiry_date == date.today() + timedelta(days=5)
        assert result.quantity == 3

    def test_bulk_dlc_no_shelf_life(self):
        """Sans shelf_life_days → expiry_date est None."""
        vlm = {"product_name": "Pommes", "quantity": 6, "confidence": 0.8}
        off = OFFData(found=False)
        images = [_make_image()]

        result = _fuse_results(None, off, vlm, is_bulk=True, images=images)

        assert result.expiry_date is None

    def test_display_image_off_url_priority(self):
        """Si OFF a une image_url, display_image l'utilise."""
        vlm = {"product_name": "Nutella", "confidence": 0.9}
        off = OFFData(found=True, product_name="Nutella", image_url="https://off.example.com/img.jpg")
        images = [_make_image()]

        result = _fuse_results("123", off, vlm, is_bulk=False, images=images)

        assert result.display_image == "https://off.example.com/img.jpg"

    def test_display_image_fallback_base64(self):
        """Sans image OFF, display_image est un data URI Base64."""
        vlm = {"product_name": "Tomates", "quantity": 4, "shelf_life_days": 7, "confidence": 0.85}
        off = OFFData(found=False)
        images = [_make_image()]

        result = _fuse_results(None, off, vlm, is_bulk=True, images=images)

        assert result.display_image is not None
        assert result.display_image.startswith("data:image/jpeg;base64,")

    def test_bulk_dlc_invalid_shelf_life(self):
        """shelf_life_days invalide → expiry_date reste None."""
        vlm = {"product_name": "???", "quantity": 1, "shelf_life_days": "abc", "confidence": 0.3}
        off = OFFData(found=False)
        images = [_make_image()]

        result = _fuse_results(None, off, vlm, is_bulk=True, images=images)

        assert result.expiry_date is None
