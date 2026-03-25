"""Fixtures partagées pour les tests."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import create_app
from app.dependencies.vlm import get_vlm, VLMContainer
from app.dependencies.mongodb import get_database


@pytest.fixture
def mock_vlm():
    """Mock du container VLM pour les tests sans GPU."""
    container = MagicMock(spec=VLMContainer)
    container.is_loaded = True
    return container


@pytest.fixture
def mock_db():
    """Mock de la base MongoDB."""
    db = MagicMock()
    collection = MagicMock()
    collection.insert_one = AsyncMock()
    collection.find = MagicMock(return_value=MagicMock(
        skip=MagicMock(return_value=MagicMock(
            limit=MagicMock(return_value=MagicMock(
                sort=MagicMock(return_value=MagicMock(
                    to_list=AsyncMock(return_value=[])
                ))
            ))
        ))
    ))
    collection.count_documents = AsyncMock(return_value=0)
    db.__getitem__ = MagicMock(return_value=collection)
    return db


@pytest.fixture
def client(mock_vlm, mock_db):
    """Client de test FastAPI avec dépendances mockées."""
    app = create_app()
    app.dependency_overrides[get_vlm] = lambda: mock_vlm
    app.dependency_overrides[get_database] = lambda: mock_db
    return TestClient(app, raise_server_exceptions=False)
