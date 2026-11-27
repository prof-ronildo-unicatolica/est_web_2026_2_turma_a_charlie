from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(case_sensitive=True, env_file=".env")

    PROJECT_NAME: str = "Sistema de Reservas - Core Service"
    API_V1_STR: str = "/api/v1"
    JWT_SECRET_KEY: str

    # Credenciais podem ser sobrescritas por variáveis de ambiente.
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "hotel_db_dev"
    POSTGRES_PORT: str = "5432"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    MONGODB_URL: str
    MONGODB_DB: str = "hotel_mongo_dev"
    MONGO_ADMIN_PASSWORD: str

    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # Em produção, defina uma chave aleatória forte via ambiente.
    SECRET_KEY: str = "dev-only-change-this-secret-key-before-deploy"
    INITIAL_ADMIN_EMAIL: str | None = None
    INITIAL_ADMIN_PASSWORD: str | None = None
    INITIAL_ADMIN_NAME: str = "Administrador"
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"


settings = Settings()
