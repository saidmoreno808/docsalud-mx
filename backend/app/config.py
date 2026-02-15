"""
Configuracion centralizada de DocSalud MX.

Usa pydantic-settings para cargar variables de entorno con validacion de tipos.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracion de la aplicacion cargada desde variables de entorno."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "docsalud-mx"
    app_env: str = "development"
    app_debug: bool = True
    app_port: int = 8000
    app_host: str = "0.0.0.0"
    secret_key: str = "change-me-in-production"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Database
    database_url: str = (
        "postgresql+asyncpg://docsalud:password@localhost:5432/docsalud_db"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo"
    openai_embedding_model: str = "text-embedding-3-small"

    # Anthropic
    anthropic_api_key: str = ""

    # Tesseract
    tesseract_cmd: str = "/usr/bin/tesseract"
    tesseract_lang: str = "spa"

    # AWS
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "docsalud-mx-documents"

    # Logging
    log_level: str = "DEBUG"
    log_format: str = "json"

    # ML Models
    model_path: str = "./models"
    ner_model_path: str = "./models/ner_medical"
    classifier_model_path: str = "./models/document_classifier"
    anomaly_model_path: str = "./models/anomaly_detector"

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna lista de origenes CORS permitidos."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
