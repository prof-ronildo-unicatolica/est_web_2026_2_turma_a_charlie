
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.core.security import criar_access_token, decodificar_access_token


def test_token_jwt_valido():
    """Token gerado com a chave correta deve ser aceito."""

    token = criar_access_token({"sub": "cliente@hotel.com"})

    resultado = decodificar_access_token(token)

    assert resultado is not None
    assert resultado["sub"] == "cliente@hotel.com"


def test_token_jwt_com_assinatura_falsa():
    """Token assinado com outra chave deve ser rejeitado."""

    payload = {
        "sub": "admin@hotel.com",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }

    token_falso = jwt.encode(
        payload,
        "chave-falsa-apenas-para-testes",
        algorithm="HS256",
    )

    assert decodificar_access_token(token_falso) is None


def test_token_jwt_expirado():
    """Token expirado não deve permitir autenticação."""

    payload = {
        "sub": "cliente@hotel.com",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
    }

    token_expirado = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    assert decodificar_access_token(token_expirado) is None
