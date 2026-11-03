"""Application configuration read from environment variables."""

from dataclasses import dataclass
import os
from pathlib import Path


def _load_env_file() -> None:
    """Populate os.environ from the workspace .env file when present."""

    possible_dirs = [
        Path.cwd(),
        Path(__file__).resolve().parent,
        Path(__file__).resolve().parent.parent,
    ]

    for directory in possible_dirs:
        env_path = directory / ".env"
        if not env_path.is_file():
            continue

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = (part.strip() for part in raw_line.split("=", 1))
            if not key or key.startswith("#"):
                continue

            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]

            os.environ.setdefault(key, value)


_load_env_file()


@dataclass(frozen=True)
class Settings:
    """Runtime settings shared by API routes and future services."""

    app_name: str = os.getenv("APP_NAME", "Intelligent ML Notes API")
    environment: str = os.getenv("ENVIRONMENT", "development")
    api_prefix: str = os.getenv("API_PREFIX", "/api")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    groq_model: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    cors_origins: str = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    )

    @property
    def allowed_origins(self) -> list[str]:
        """Return normalized browser origins for local frontend development."""

        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def llm_provider(self) -> str:
        """Prefer the provider whose API key is configured; default to Gemini for compatibility."""

        if self.gemini_api_key:
            return "gemini"
        if self.groq_api_key:
            return "groq"
        return "gemini"


settings = Settings()
