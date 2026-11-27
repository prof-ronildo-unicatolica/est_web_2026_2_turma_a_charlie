
from app.core.security import (
    criar_access_token,
    decodificar_access_token,
    hash_senha,
    verificar_senha,
)


def test_hash_senha():
    senha = "SenhaTeste123"

    resultado = hash_senha(senha)

    assert resultado != senha
    assert verificar_senha(senha, resultado)


def test_verificar_senha_incorreta():
    senha_hash = hash_senha("SenhaCorreta123")

    assert verificar_senha("SenhaErrada123", senha_hash) is False


def test_criar_access_token():
    dados = {"sub": "cliente@hotel.com"}

    token = criar_access_token(dados)

    assert isinstance(token, str)
    assert token


def test_decodificar_access_token_valido():
    dados = {"sub": "cliente@hotel.com"}

    token = criar_access_token(dados)
    resultado = decodificar_access_token(token)

    assert resultado["sub"] == "cliente@hotel.com"
    assert "exp" in resultado


def test_decodificar_access_token_invalido():
    resultado = decodificar_access_token("token_invalido")

    assert resultado is None
