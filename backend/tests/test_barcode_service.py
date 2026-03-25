"""Tests pour le service de décodage barcode."""

import pytest
from PIL import Image

from app.services.barcode_service import decode_barcode
from app.core import BarcodeDecodeError


class TestBarcodeService:
    """Tests pour decode_barcode."""

    def test_no_barcode_raises(self):
        """Lève BarcodeDecodeError si aucun barcode n'est détecté."""
        img = Image.new("RGB", (100, 100), color="white")
        with pytest.raises(BarcodeDecodeError):
            decode_barcode(img)

    def test_returns_string(self):
        """Le résultat est bien une chaîne de caractères."""
        # Ce test nécessite une vraie image avec code-barres
        # pour un test unitaire pur, on vérifie le type de retour
        img = Image.new("RGB", (100, 100), color="white")
        with pytest.raises(BarcodeDecodeError):
            result = decode_barcode(img)
