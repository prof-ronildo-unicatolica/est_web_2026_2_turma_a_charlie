import asyncio
from unittest.mock import AsyncMock, Mock

import app.services.catalogo_service as catalogo_module
from app.services.catalogo_service import CatalogoService


def criar_service(monkeypatch):
    repository = Mock()

    repository.salvar_hotel = AsyncMock()
    repository.listar_hoteis = AsyncMock(return_value=[])
    repository.buscar_por_cidade = AsyncMock(return_value=[])
    repository.remover_hotel = AsyncMock()

    monkeypatch.setattr(
        catalogo_module,
        "CatalogoRepository",
        lambda db: repository,
    )

    service = CatalogoService(db=Mock())

    return service, repository


def test_salvar_hotel(monkeypatch):
    service, repository = criar_service(monkeypatch)
    hotel = {"hotel_id": "123", "nome": "Hotel Central"}

    asyncio.run(service.salvar_hotel(hotel))

    repository.salvar_hotel.assert_awaited_once_with(hotel)


def test_listar_hoteis(monkeypatch):
    service, repository = criar_service(monkeypatch)
    hoteis = [{"nome": "Hotel Central"}]
    repository.listar_hoteis.return_value = hoteis

    resultado = asyncio.run(service.listar_hoteis())

    repository.listar_hoteis.assert_awaited_once_with()
    assert resultado == hoteis


def test_buscar_por_cidade(monkeypatch):
    service, repository = criar_service(monkeypatch)
    hoteis = [{"nome": "Hotel Central"}]
    repository.buscar_por_cidade.return_value = hoteis

    resultado = asyncio.run(
        service.buscar_por_cidade("cidade-123")
    )

    repository.buscar_por_cidade.assert_awaited_once_with(
        "cidade-123"
    )
    assert resultado == hoteis


def test_remover_hotel(monkeypatch):
    service, repository = criar_service(monkeypatch)

    asyncio.run(service.remover_hotel("hotel-123"))

    repository.remover_hotel.assert_awaited_once_with("hotel-123")