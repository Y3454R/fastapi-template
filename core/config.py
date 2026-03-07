import os
from dotenv import load_dotenv

# Load .env file (for local development)
load_dotenv()


def _require(key: str) -> str:
    """Return the value of *key* from the environment, or raise if missing."""
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def _get_bool(key: str, default: str = "false") -> bool:
    """Parse a boolean environment variable. Accepts 'true', '1', 'yes'."""
    return os.getenv(key, default).lower() in ("true", "1", "yes")


def _get_optional(key: str, default: str = "") -> str:
    """Return the value of *key*, or *default* if unset (no error raised)."""
    return os.getenv(key, default)


class Settings:
    # ------------------------------
    # Server
    # ------------------------------
    port: int = int(_require("PORT"))

    # ------------------------------
    # Application
    # ------------------------------
    app_name: str = os.getenv("APP_NAME", "FastAPI Template")
    api_prefix: str = _require("API_PREFIX")
    debug: bool = _get_bool("DEBUG")

    # ------------------------------
    # CORS
    # ------------------------------
    cors_frontend_url: str = _require("FRONTEND_URL")
    cors_admin_url: str = _require("ADMIN_URL")

    @property
    def cors_origins(self) -> list[str]:
        """Allowed CORS origins derived from env vars."""
        return [
            self.cors_frontend_url,
            self.cors_admin_url,
        ]

    # ------------------------------
    # Database
    # ------------------------------
    db_username: str = _require("DB_USERNAME")
    db_password: str = _require("DB_PASSWORD")
    db_host: str = _require("DB_HOST")
    db_port: str = _require("DB_PORT")
    db_name: str = _require("DB_NAME")

    @property
    def database_url(self) -> str:
        """Full PostgreSQL connection string built from individual DB settings."""
        return (
            f"postgresql://{self.db_username}:"
            f"{self.db_password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}"
        )

    # ------------------------------
    # JWT
    # ------------------------------
    jwt_secret_key: str = _require("JWT_SECRET_KEY")
    jwt_algorithm: str = _require("JWT_ALGORITHM")
    access_token_expire_minutes: int = int(_require("ACCESS_TOKEN_EXPIRE_MINUTES"))

    # ------------------------------
    # Static / Public Assets
    # ------------------------------
    static_dir: str = os.getenv("STATIC_DIR", "static")
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

    # ------------------------------
    # AI Services
    # ------------------------------
    openai_api_key: str = _get_optional("OPENAI_API_KEY")
    """OpenAI API key. Leave blank to disable AI endpoints gracefully."""


settings = Settings()