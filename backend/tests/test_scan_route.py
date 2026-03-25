"""Tests pour la route POST /scan."""

import io
from PIL import Image


def _create_test_image(width: int = 100, height: int = 100) -> bytes:
    """Crée une image de test en mémoire."""
    img = Image.new("RGB", (width, height), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer.getvalue()


class TestScanRoute:
    """Tests pour POST /api/v1/scan."""

    def test_scan_no_images(self, client):
        """Rejette une requête sans images."""
        response = client.post("/api/v1/scan")
        assert response.status_code == 422

    def test_scan_invalid_image(self, client):
        """Rejette un fichier non-image."""
        response = client.post(
            "/api/v1/scan",
            files=[("images", ("test.txt", b"not an image", "text/plain"))],
        )
        assert response.status_code == 422

    def test_scan_accepts_valid_image(self, client, mock_vlm, monkeypatch):
        """Accepte une image valide et appelle le pipeline."""
        from app.services import scan_orchestrator
        from app.schemas.scan import ScanResponse

        mock_response = ScanResponse(
            product_name="Test",
            source="vlm",
            confidence=0.9,
        )

        async def mock_process_scan(**kwargs):
            return mock_response

        monkeypatch.setattr(scan_orchestrator, "process_scan", mock_process_scan)

        image_bytes = _create_test_image()
        response = client.post(
            "/api/v1/scan",
            files=[("images", ("test.jpg", image_bytes, "image/jpeg"))],
            data={"is_bulk": "false"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["product_name"] == "Test"
        assert data["source"] == "vlm"

    def test_scan_bulk_flag(self, client, monkeypatch):
        """Passe le flag is_bulk au pipeline."""
        from app.services import scan_orchestrator
        from app.schemas.scan import ScanResponse

        captured_kwargs = {}

        async def mock_process_scan(**kwargs):
            captured_kwargs.update(kwargs)
            return ScanResponse(
                product_name="Bananes",
                quantity=4,
                source="vlm",
                confidence=0.85,
            )

        monkeypatch.setattr(scan_orchestrator, "process_scan", mock_process_scan)

        image_bytes = _create_test_image()
        response = client.post(
            "/api/v1/scan",
            files=[("images", ("fruit.jpg", image_bytes, "image/jpeg"))],
            data={"is_bulk": "true"},
        )

        assert response.status_code == 200
        assert response.json()["quantity"] == 4
