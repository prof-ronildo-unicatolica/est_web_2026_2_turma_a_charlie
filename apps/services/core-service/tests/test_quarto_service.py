import asyncio
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import app.services.quarto_service as quarto_service_module
from app.services.quarto_service import QuartoService


def criar_service(monkeypatch):
    repository = Mock()
    catalogo_sync = Mock()
    catalogo_sync.sincronizar_hotel = AsyncMock()

    monkeypatch.setattr(
        quarto_service_module,
        "QuartoRepository",
        lambda db: repository,
    )

    monkeypatch.setattr(
        quarto_service_module,
        "CatalogoSyncService",
        lambda db, mongo_db: catalogo_sync,
    )

    service = QuartoService(
        db=Mock(),
        mongo_db=Mock(),
    )

    return service, repository, catalogo_sync


def criar_payload():
    return SimpleNamespace(
        hotel_id="hotel-123",
        tipo="Luxo",
        preco_diaria=Decimal("250.00"),
        max_adultos=2,
        max_criancas=1,
    )


def test_create_quarto_e_sincroniza_catalogo(monkeypatch):
    service, repository, catalogo_sync = criar_service(monkeypatch)
    payload = criar_payload()
    quarto = SimpleNamespace(hotel_id=payload.hotel_id)

    repository.create.return_value = quarto

    resultado = asyncio.run(service.create(payload))

    repository.create.assert_called_once_with(
        hotel_id=payload.hotel_id,
        tipo=payload.tipo,
        preco_diaria=payload.preco_diaria,
        max_adultos=payload.max_adultos,
        max_criancas=payload.max_criancas,
    )

    catalogo_sync.sincronizar_hotel.assert_awaited_once_with(
        payload.hotel_id
    )

    assert resultado is quarto


def test_list_retorna_quartos(monkeypatch):
    service, repository, _ = criar_service(monkeypatch)
    quartos = [Mock(), Mock()]

    repository.list.return_value = quartos

    resultado = service.list()

    repository.list.assert_called_once_with()
    assert resultado == quartos


def test_get_by_id_retorna_quarto(monkeypatch):
    service, repository, _ = criar_service(monkeypatch)
    quarto = Mock()

    repository.get_by_id.return_value = quarto

    resultado = service.get_by_id("quarto-123")

    repository.get_by_id.assert_called_once_with("quarto-123")
    assert resultado is quarto


def test_update_quarto_inexistente(monkeypatch):
    service, repository, catalogo_sync = criar_service(monkeypatch)

    repository.get_by_id.return_value = None
    payload = Mock()

    resultado = asyncio.run(
        service.update("quarto-inexistente", payload)
    )

    assert resultado is None
    repository.update.assert_not_called()
    catalogo_sync.sincronizar_hotel.assert_not_awaited()


def test_update_quarto_existente(monkeypatch):
    service, repository, catalogo_sync = criar_service(monkeypatch)

    quarto = SimpleNamespace(hotel_id="hotel-123")
    payload = Mock()
    dados = {"tipo": "Premium"}
    payload.model_dump.return_value = dados

    repository.get_by_id.return_value = quarto
    repository.update.return_value = quarto

    resultado = asyncio.run(
        service.update("quarto-123", payload)
    )

    payload.model_dump.assert_called_once_with(exclude_unset=True)
    repository.update.assert_called_once_with(quarto, dados)

    catalogo_sync.sincronizar_hotel.assert_awaited_once_with(
        quarto.hotel_id
    )

    assert resultado is quarto


def test_delete_quarto_inexistente(monkeypatch):
    service, repository, catalogo_sync = criar_service(monkeypatch)

    repository.get_by_id.return_value = None

    resultado = asyncio.run(service.delete("quarto-inexistente"))

    assert resultado is None
    repository.delete.assert_not_called()
    catalogo_sync.sincronizar_hotel.assert_not_awaited()


def test_delete_quarto_existente(monkeypatch):
    service, repository, catalogo_sync = criar_service(monkeypatch)

    quarto = SimpleNamespace(hotel_id="hotel-123")
    repository.get_by_id.return_value = quarto

    resultado = asyncio.run(service.delete("quarto-123"))

    repository.delete.assert_called_once_with(quarto)

    catalogo_sync.sincronizar_hotel.assert_awaited_once_with(
        quarto.hotel_id
    )

    assert resultado is quarto
    