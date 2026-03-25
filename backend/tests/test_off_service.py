"""Tests pour le service OpenFoodFacts."""

import pytest
import httpx

from app.services.off_service import fetch_product


class TestOFFService:
    """Tests pour fetch_product."""

    @pytest.mark.asyncio
    async def test_product_not_found(self, monkeypatch):
        """Retourne found=False quand le produit n'existe pas."""

        async def mock_get(*args, **kwargs):
            response = httpx.Response(
                200,
                json={"status": 0},
                request=httpx.Request("GET", "http://test"),
            )
            return response

        monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

        result = await fetch_product("0000000000000")
        assert result.found is False

    @pytest.mark.asyncio
    async def test_product_found(self, monkeypatch):
        """Retourne les données OFF quand le produit existe."""

        async def mock_get(*args, **kwargs):
            response = httpx.Response(
                200,
                json={
                    "status": 1,
                    "product": {
                        "product_name": "Nutella",
                        "brands": "Ferrero",
                        "image_url": "https://images.off.org/nutella.jpg",
                        "categories": "Pâtes à tartiner",
                        "nutriscore_grade": "e",
                    },
                },
                request=httpx.Request("GET", "http://test"),
            )
            return response

        monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

        result = await fetch_product("3017620422003")
        assert result.found is True
        assert result.product_name == "Nutella"
        assert result.brand == "Ferrero"

    @pytest.mark.asyncio
    async def test_network_error_returns_not_found(self, monkeypatch):
        """Retourne found=False en cas d'erreur réseau."""

        async def mock_get(*args, **kwargs):
            raise httpx.TimeoutException("Timeout")

        monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

        result = await fetch_product("3017620422003")
        assert result.found is False
