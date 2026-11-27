
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.seed_mongo import seed_mongo_users


@pytest.mark.anyio
async def test_cria_usuario_admin_quando_nao_existe():
    db = MagicMock()
    collection = MagicMock()

    db.__getitem__.return_value = collection
    collection.find_one = AsyncMock(return_value=None)
    collection.insert_one = AsyncMock()

    with patch(
        "app.core.seed_mongo.pwd_context.hash",
        return_value="senha_criptografada",
    ) as hash_mock:
        await seed_mongo_users(db)

    hash_mock.assert_called_once()

    collection.find_one.assert_awaited_once_with(
        {"email": "admin@hotel.com"}
    )

    collection.insert_one.assert_awaited_once()

    usuario = collection.insert_one.call_args.args[0]

    assert usuario["username"] == "admin"
    assert usuario["email"] == "admin@hotel.com"
    assert usuario["password_hash"] == "senha_criptografada"
    assert usuario["role"] == "admin_master"
    assert usuario["active"] is True


@pytest.mark.anyio
async def test_nao_cria_usuario_admin_se_ja_existe():
    db = MagicMock()
    collection = MagicMock()

    db.__getitem__.return_value = collection
    collection.find_one = AsyncMock(
        return_value={"email": "admin@hotel.com"}
    )
    collection.insert_one = AsyncMock()

    await seed_mongo_users(db)

    collection.find_one.assert_awaited_once_with(
        {"email": "admin@hotel.com"}
    )

    collection.insert_one.assert_not_awaited()


@pytest.mark.anyio
async def test_registra_erro_quando_falha_no_seed(caplog):
    db = MagicMock()
    collection = MagicMock()

    db.__getitem__.return_value = collection
    collection.find_one = AsyncMock(
        side_effect=Exception("Erro de conexão")
    )

    await seed_mongo_users(db)

    assert "MongoDB seed falhou" in caplog.text
    assert "Erro de conexão" in caplog.text
