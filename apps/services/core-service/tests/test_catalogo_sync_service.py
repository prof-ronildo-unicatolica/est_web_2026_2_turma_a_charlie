import asyncio
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import app.services.catalogo_sync_service as sync_module
from app.services.catalogo_sync_service import CatalogoSyncService


def criar_service(monkeypatch, hotel=None):
    hotel_repository = Mock()
    hotel_repository.get_by_id.return_value = hotel

    catalogo_repository = Mock()
    catalogo_repository.salvar_hotel = AsyncMock()
    catalogo_repository.remover_hotel = AsyncMock()

    monkeypatch.setattr(
        sync_module,
        "HotelRepository",
        lambda db: hotel_repository,
    )

    monkeypatch.setattr(
        sync_module,
        "CatalogoRepository",
        lambda mongo_db: catalogo_repository,
    )

    service = CatalogoSyncService(
        db=Mock(),
        mongo_db=Mock(),
    )

    return service, hotel_repository, catalogo_repository


def test_sincronizar_hotel_inexistente_remove_catalogo(monkeypatch):
    service, hotel_repository, catalogo_repository = criar_service(
        monkeypatch
    )

    asyncio.run(service.sincronizar_hotel("hotel-123"))

    hotel_repository.get_by_id.assert_called_once_with("hotel-123")

    catalogo_repository.remover_hotel.assert_awaited_once_with(
        "hotel-123"
    )

    catalogo_repository.salvar_hotel.assert_not_awaited()


def test_sincronizar_hotel_existente_com_quartos(monkeypatch):
    quarto = SimpleNamespace(
        id="quarto-123",
        tipo="Luxo",
        preco_diaria=Decimal("250.50"),
        max_adultos=2,
        max_criancas=1,
    )

    hotel = SimpleNamespace(
        id="hotel-123",
        nome="Hotel Central",
        categoria_estrelas=4,
        cidade=SimpleNamespace(
            id="cidade-123",
            nome="Fortaleza",
            estado="CE",
        ),
        quartos=[quarto],
    )

    service, hotel_repository, catalogo_repository = criar_service(
        monkeypatch,
        hotel,
    )

    asyncio.run(service.sincronizar_hotel("hotel-123"))

    documento_esperado = {
        "hotel_id": "hotel-123",
        "nome": "Hotel Central",
        "categoria_estrelas": 4,
        "cidade_id": "cidade-123",
        "cidade_nome": "Fortaleza",
        "cidade_estado": "CE",
        "quartos": [
            {
                "quarto_id": "quarto-123",
                "tipo": "Luxo",
                "preco_diaria": 250.50,
                "max_adultos": 2,
                "max_criancas": 1,
            }
        ],
    }

    hotel_repository.get_by_id.assert_called_once_with("hotel-123")

    catalogo_repository.salvar_hotel.assert_awaited_once_with(
        documento_esperado
    )

    catalogo_repository.remover_hotel.assert_not_awaited()


def test_sincronizar_hotel_sem_quartos(monkeypatch):
    hotel = SimpleNamespace(
        id="hotel-456",
        nome="Hotel sem Quartos",
        categoria_estrelas=3,
        cidade=SimpleNamespace(
            id="cidade-456",
            nome="Quixadá",
            estado="CE",
        ),
        quartos=[],
    )

    service, _, catalogo_repository = criar_service(
        monkeypatch,
        hotel,
    )

    asyncio.run(service.sincronizar_hotel("hotel-456"))

    documento = catalogo_repository.salvar_hotel.await_args.args[0]

    assert documento["hotel_id"] == "hotel-456"
    assert documento["quartos"] == []