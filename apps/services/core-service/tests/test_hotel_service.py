import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import app.services.hotel_service as hotel_module
from app.services.hotel_service import CidadeService, HotelService


def criar_cidade_service(monkeypatch):
    repository = Mock()

    monkeypatch.setattr(
        hotel_module,
        "CidadeRepository",
        lambda db: repository,
    )

    service = CidadeService(db=Mock())

    return service, repository


def criar_hotel_service(monkeypatch):
    repository = Mock()
    catalogo_sync = Mock()
    catalogo_sync.sincronizar_hotel = AsyncMock()

    monkeypatch.setattr(
        hotel_module,
        "HotelRepository",
        lambda db: repository,
    )

    monkeypatch.setattr(
        hotel_module,
        "CatalogoSyncService",
        lambda db, mongo_db: catalogo_sync,
    )

    service = HotelService(
        db=Mock(),
        mongo_db=Mock(),
    )

    return service, repository, catalogo_sync


def test_criar_cidade(monkeypatch):
    service, repository = criar_cidade_service(monkeypatch)

    payload = SimpleNamespace(
        nome="Fortaleza",
        estado="CE",
    )

    cidade = Mock()
    repository.create.return_value = cidade

    resultado = service.create(payload)

    repository.create.assert_called_once_with(
        nome="Fortaleza",
        estado="CE",
    )

    assert resultado is cidade


def test_listar_cidades(monkeypatch):
    service, repository = criar_cidade_service(monkeypatch)

    cidades = [Mock(), Mock()]
    repository.list.return_value = cidades

    resultado = service.list()

    repository.list.assert_called_once_with()
    assert resultado == cidades


def test_buscar_cidade_por_id(monkeypatch):
    service, repository = criar_cidade_service(monkeypatch)

    cidade = Mock()
    repository.get_by_id.return_value = cidade

    resultado = service.get_by_id("cidade-123")

    repository.get_by_id.assert_called_once_with("cidade-123")
    assert resultado is cidade


def test_buscar_cidade_por_nome(monkeypatch):
    service, repository = criar_cidade_service(monkeypatch)

    cidade = Mock()
    repository.get_by_nome.return_value = cidade

    resultado = service.get_by_nome("Fortaleza")

    repository.get_by_nome.assert_called_once_with("Fortaleza")
    assert resultado is cidade


def test_criar_hotel_com_comodidades(monkeypatch):
    service, repository, catalogo_sync = criar_hotel_service(
        monkeypatch
    )

    comodidades = [
        SimpleNamespace(id=1),
        SimpleNamespace(id=2),
    ]

    repository.get_comodidades_by_ids.return_value = comodidades

    payload = SimpleNamespace(
        nome="Hotel Central",
        cidade_id="cidade-123",
        categoria_estrelas=4,
        comodidade_ids=[1, 2],
    )

    hotel = SimpleNamespace(id="hotel-123")
    repository.create.return_value = hotel

    resultado = asyncio.run(service.create(payload))

    repository.get_comodidades_by_ids.assert_called_once_with([1, 2])

    repository.create.assert_called_once_with(
        nome="Hotel Central",
        cidade_id="cidade-123",
        categoria_estrelas=4,
        comodidades=comodidades,
    )

    catalogo_sync.sincronizar_hotel.assert_awaited_once_with(
        "hotel-123"
    )

    assert resultado is hotel


def test_criar_hotel_com_comodidade_inexistente(monkeypatch):
    service, repository, catalogo_sync = criar_hotel_service(
        monkeypatch
    )

    repository.get_comodidades_by_ids.return_value = [
        SimpleNamespace(id=1)
    ]

    payload = SimpleNamespace(
        nome="Hotel Central",
        cidade_id="cidade-123",
        categoria_estrelas=4,
        comodidade_ids=[1, 99],
    )

    try:
        asyncio.run(service.create(payload))
        assert False, "Era esperada uma exceção ValueError."
    except ValueError as erro:
        assert "99" in str(erro)

    repository.create.assert_not_called()
    catalogo_sync.sincronizar_hotel.assert_not_awaited()


def test_listar_hoteis(monkeypatch):
    service, repository, _ = criar_hotel_service(monkeypatch)

    hoteis = [Mock(), Mock()]
    repository.list.return_value = hoteis

    resultado = service.list()

    repository.list.assert_called_once_with()
    assert resultado == hoteis


def test_listar_hoteis_por_cidade(monkeypatch):
    service, repository, _ = criar_hotel_service(monkeypatch)

    hoteis = [Mock()]
    repository.list_by_cidade.return_value = hoteis

    resultado = service.list_by_cidade("cidade-123")

    repository.list_by_cidade.assert_called_once_with("cidade-123")
    assert resultado == hoteis


def test_buscar_hotel_por_id(monkeypatch):
    service, repository, _ = criar_hotel_service(monkeypatch)

    hotel = Mock()
    repository.get_by_id.return_value = hotel

    resultado = service.get_by_id("hotel-123")

    repository.get_by_id.assert_called_once_with("hotel-123")
    assert resultado is hotel