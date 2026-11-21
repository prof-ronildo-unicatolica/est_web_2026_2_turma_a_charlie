
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import (
    autenticar_credenciais,
    get_current_user,
)


def test_autenticar_credenciais_usuario_inexistente():
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = None

    resultado = autenticar_credenciais(
        "inexistente@hotel.com",
        "senha123",
        db,
    )

    assert resultado is None


def test_autenticar_credenciais_senha_incorreta():
    db = MagicMock()
    usuario = SimpleNamespace(senha_hash="hash_teste")

    db.execute.return_value.scalar_one_or_none.return_value = usuario

    with patch(
        "app.api.deps.verificar_senha",
        return_value=False,
    ):
        resultado = autenticar_credenciais(
            "cliente@hotel.com",
            "senha_errada",
            db,
        )

    assert resultado is None


def test_get_current_user_token_invalido():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="token_invalido",
    )

    with patch(
        "app.api.deps.decodificar_access_token",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as erro:
            get_current_user(credentials, MagicMock())

    assert erro.value.status_code == 401


def test_get_current_user_token_sem_email():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="token_sem_email",
    )

    with patch(
        "app.api.deps.decodificar_access_token",
        return_value={"role": "admin"},
    ):
        with pytest.raises(HTTPException) as erro:
            get_current_user(credentials, MagicMock())

    assert erro.value.status_code == 401


def test_get_current_user_usuario_nao_encontrado():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="token_valido",
    )

    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = None

    with patch(
        "app.api.deps.decodificar_access_token",
        return_value={"sub": "inexistente@hotel.com"},
    ):
        with pytest.raises(HTTPException) as erro:
            get_current_user(credentials, db)

    assert erro.value.status_code == 401


from app.api.deps import get_current_admin


def test_autenticar_credenciais_senha_correta():
    db = MagicMock()
    usuario = SimpleNamespace(senha_hash="hash_teste")

    db.execute.return_value.scalar_one_or_none.return_value = usuario

    with patch(
        "app.api.deps.verificar_senha",
        return_value=True,
    ):
        resultado = autenticar_credenciais(
            "cliente@hotel.com",
            "senha_correta",
            db,
        )

    assert resultado is usuario


def test_get_current_user_retorna_usuario():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="token_valido",
    )

    usuario = SimpleNamespace(email="cliente@hotel.com")
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = usuario

    with patch(
        "app.api.deps.decodificar_access_token",
        return_value={"sub": "cliente@hotel.com"},
    ):
        resultado = get_current_user(credentials, db)

    assert resultado is usuario


def test_get_current_admin_bloqueia_cliente():
    usuario = SimpleNamespace(is_admin=False)

    with pytest.raises(HTTPException) as erro:
        get_current_admin(usuario)

    assert erro.value.status_code == 403


def test_get_current_admin_permite_administrador():
    usuario = SimpleNamespace(is_admin=True)

    resultado = get_current_admin(usuario)

    assert resultado is usuario
