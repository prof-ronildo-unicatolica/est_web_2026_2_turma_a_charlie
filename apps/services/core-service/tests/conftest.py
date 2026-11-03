import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.main import app
from app.models.tutorial import Base
from app.models.usuario import Usuario
from app.core.security import hash_senha

# Banco SQLite em arquivo temporario para os testes
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
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


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()
