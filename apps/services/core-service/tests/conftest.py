
from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.security import hash_senha
from app.main import app
from app.models.hotel import Cidade, Hotel, Quarto  # noqa: F401
from app.models.tutorial import Base
from app.models.usuario import Usuario


@pytest.fixture(scope="function")
def db_session():
    # SQLite em memoria: isolado do PostgreSQL.
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    cliente = Usuario(
        nome="Cliente Teste",
        email="cliente@hotel.com",
        senha_hash=hash_senha("cliente123"),
        is_admin=False,
    )

    administrador = Usuario(
        nome="Administrador Teste",
        email="admin@hotel.com",
        senha_hash=hash_senha("admin123"),
        is_admin=True,
    )

    try:
        db.add_all([cliente, administrador])
        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    # Impede o seed e a sincronizacao com MongoDB
    # durante a inicializacao do TestClient.
    @asynccontextmanager
    async def lifespan_teste(_app):
        yield

    monkeypatch.setattr(
        app.router,
        "lifespan_context",
        lifespan_teste,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(
            app,
            raise_server_exceptions=False,
        ) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
