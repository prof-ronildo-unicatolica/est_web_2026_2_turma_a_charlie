
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.catalogo_repository import CatalogoRepository


@pytest.fixture
def mongo_mock():
    db = MagicMock()
    collection = MagicMock()
    db.__getitem__.return_value = collection

    return db, collection


@pytest.mark.anyio
async def test_salvar_hotel(mongo_mock):
    db, collection = mongo_mock
    collection.update_one = AsyncMock()

    repository = CatalogoRepository(db)
    hotel = {"hotel_id": "123", "nome": "Hotel Teste"}

    await repository.salvar_hotel(hotel)

    collection.update_one.assert_awaited_once_with(
        {"hotel_id": "123"},
        {"$set": hotel},
        upsert=True,
    )


@pytest.mark.anyio
async def test_listar_hoteis(mongo_mock):
    db, collection = mongo_mock
    cursor = MagicMock()
    cursor.to_list = AsyncMock(return_value=[
        {"hotel_id": "123", "nome": "Hotel Teste"}
    ])
    collection.find.return_value = cursor

    repository = CatalogoRepository(db)

    resultado = await repository.listar_hoteis()

    assert resultado == [{"hotel_id": "123", "nome": "Hotel Teste"}]
    collection.find.assert_called_once_with({}, {"_id": 0})
    cursor.to_list.assert_awaited_once_with(length=None)


@pytest.mark.anyio
async def test_buscar_por_filtros(mongo_mock):
    db, collection = mongo_mock
    cursor = MagicMock()
    cursor.to_list = AsyncMock(return_value=[
        {"hotel_id": "123", "cidade_id": "456"}
    ])
    collection.find.return_value = cursor

    repository = CatalogoRepository(db)
    filtros = {"cidade_id": "456"}

    resultado = await repository.buscar(filtros)

    assert resultado == [{"hotel_id": "123", "cidade_id": "456"}]
    collection.find.assert_called_once_with(filtros, {"_id": 0})


@pytest.mark.anyio
async def test_buscar_por_cidade(mongo_mock):
    db, collection = mongo_mock
    cursor = MagicMock()
    cursor.to_list = AsyncMock(return_value=[
        {"hotel_id": "123", "cidade_id": "456"}
    ])
    collection.find.return_value = cursor

    repository = CatalogoRepository(db)

    resultado = await repository.buscar_por_cidade("456")

    assert resultado == [{"hotel_id": "123", "cidade_id": "456"}]
    collection.find.assert_called_once_with(
        {"cidade_id": "456"},
        {"_id": 0},
    )


@pytest.mark.anyio
async def test_remover_hotel(mongo_mock):
    db, collection = mongo_mock
    collection.delete_one = AsyncMock()

    repository = CatalogoRepository(db)

    await repository.remover_hotel("123")

    collection.delete_one.assert_awaited_once_with(
        {"hotel_id": "123"},
    )
