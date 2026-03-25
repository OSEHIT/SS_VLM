"""Tests pour le service VLM."""

from app.services.vlm_service import _parse_vlm_output


class TestVLMParsing:
    """Tests pour le parsing de la sortie VLM."""

    def test_parse_clean_json(self):
        """Parse un JSON propre."""
        raw = '{"product_name": "Yaourt", "confidence": 0.9}'
        result = _parse_vlm_output(raw)
        assert result["product_name"] == "Yaourt"
        assert result["confidence"] == 0.9
        assert result["raw"] == raw

    def test_parse_json_with_fences(self):
        """Parse un JSON entouré de markdown fences."""
        raw = '```json\n{"expiry_date": "2025-06-15", "confidence": 0.85}\n```'
        result = _parse_vlm_output(raw)
        assert result["expiry_date"] == "2025-06-15"
        assert result["confidence"] == 0.85

    def test_parse_json_with_text_before(self):
        """Parse un JSON précédé de texte."""
        raw = 'Here is the result: {"product_name": "Lait", "brand": "Lactel"}'
        result = _parse_vlm_output(raw)
        assert result["product_name"] == "Lait"
        assert result["brand"] == "Lactel"

    def test_parse_invalid_json(self):
        """Retourne parse_error=True si le JSON est invalide."""
        raw = "This is not JSON at all"
        result = _parse_vlm_output(raw)
        assert result.get("parse_error") is True
        assert result["raw"] == raw

    def test_parse_empty_string(self):
        """Gère une chaîne vide."""
        result = _parse_vlm_output("")
        assert result.get("parse_error") is True
