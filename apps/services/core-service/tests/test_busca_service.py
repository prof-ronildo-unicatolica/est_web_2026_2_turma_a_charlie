import asyncio
from unittest.mock import AsyncMock, Mock

import app.services.busca_service as busca_service_module
from app.services.busca_service import BuscaService


def criar_service(monkeypatch):
    repository = Mock()
    repository.buscar = AsyncMock(return_value=[])

    monkeypatch.setattr(
        busca_service_module,
        "CatalogoRepository",
        lambda db: repository,
    )

    service = BuscaService(db=Mock())

    return service, repository


def test_buscar_hoteis_sem_filtros(monkeypatch):
    service, repository = criar_service(monkeypatch)

    resultado = asyncio.run(service.buscar_hoteis())

    repository.buscar.assert_awaited_once_with({})
    assert resultado == []


def test_buscar_hoteis_por_cidade(monkeypatch):
    service, repository = criar_service(monkeypatch)

    hoteis = [{"nome": "Hotel Central"}]
    repository.buscar.return_value = hoteis

    resultado = asyncio.run(
        service.buscar_hoteis(cidade_id="cidade-123")
    )

    repository.buscar.assert_awaited_once_with(
        {"cidade_id": "cidade-123"}
    )
    assert resultado == hoteis


def test_buscar_hoteis_por_estrelas(monkeypatch):
    service, repository = criar_service(monkeypatch)

    hoteis = [{"nome": "Hotel 5 Estrelas"}]
    repository.buscar.return_value = hoteis

    resultado = asyncio.run(
        service.buscar_hoteis(estrelas=5)
    )

    repository.buscar.assert_awaited_once_with(
        {"categoria_estrelas": 5}
    )
    assert resultado == hoteis


def test_buscar_hoteis_por_cidade_e_estrelas(monkeypatch):
    service, repository = criar_service(monkeypatch)

    hoteis = [{"nome": "Hotel Central"}]
    repository.buscar.return_value = hoteis

    resultado = asyncio.run(
        service.buscar_hoteis(
            cidade_id="cidade-123",
            estrelas=4,
        )
    )

    repository.buscar.assert_awaited_once_with(
        {
            "cidade_id": "cidade-123",
            "categoria_estrelas": 4,
        }
    )
    assert resultado == hoteis