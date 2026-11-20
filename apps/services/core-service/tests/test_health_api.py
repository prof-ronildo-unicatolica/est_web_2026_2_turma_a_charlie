
from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db, get_mongo_db


@pytest.fixture
def health_client():
    db_mock = MagicMock()
    mongo_mock = MagicMock()
    mongo_mock.command = AsyncMock()

    app.dependency_overrides[get_db] = lambda: db_mock
    app.dependency_overrides[get_mongo_db] = lambda: mongo_mock

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, db_mock, mongo_mock

    app.dependency_overrides.clear()


def test_health_com_bancos_funcionando(health_client):
    client, db_mock, mongo_mock = health_client

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "postgres": "healthy",
        "mongodb": "healthy",
    }

    db_mock.execute.assert_called_once()
    mongo_mock.command.assert_awaited_once_with("ping")


def test_health_com_erro_no_postgres(health_client):
    client, db_mock, mongo_mock = health_client

    db_mock.execute.side_effect = Exception("Erro no PostgreSQL")

    response = client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json()["detail"]["status"] == "unhealthy"
    assert "Erro no PostgreSQL" in response.json()["detail"]["postgres"]
    assert response.json()["detail"]["mongodb"] == "healthy"


def test_health_com_erro_no_mongodb(health_client):
    client, db_mock, mongo_mock = health_client

    mongo_mock.command.side_effect = Exception("Erro no MongoDB")

    response = client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json()["detail"]["status"] == "unhealthy"
    assert response.json()["detail"]["postgres"] == "healthy"
    assert "Erro no MongoDB" in response.json()["detail"]["mongodb"]


def test_health_com_erro_nos_dois_bancos(health_client):
    client, db_mock, mongo_mock = health_client

    db_mock.execute.side_effect = Exception("Erro no PostgreSQL")
    mongo_mock.command.side_effect = Exception("Erro no MongoDB")

    response = client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json()["detail"]["status"] == "unhealthy"
    assert "Erro no PostgreSQL" in response.json()["detail"]["postgres"]
    assert "Erro no MongoDB" in response.json()["detail"]["mongodb"]
