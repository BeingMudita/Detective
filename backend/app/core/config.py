"""Application configuration.

Everything is environment-driven with safe local defaults. Notably, if
``SECRET_KEY`` is not supplied we generate one and persist it to a local,
gitignored file so JWTs stay valid across restarts — no external key service,
no manual setup, zero cost.
"""
from __future__ import annotations

import secrets
from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/  (…/app/core/config.py -> parents[2])
_BACKEND_DIR = Path(__file__).resolve().parents[2]
_SECRET_FILE = _BACKEND_DIR / ".secret_key"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=True
    )

    # ── meta ──
    PROJECT_NAME: str = "Internet Detective"
    API_V1_PREFIX: str = "/api/v1"
    ENV: str = "development"

    # ── database ──
    DATABASE_URL: str = "postgresql+asyncpg://detective:detective@localhost:5432/detective"

    # ── auth ──
    SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    REFRESH_COOKIE_NAME: str = "id_refresh"
    REFRESH_COOKIE_SECURE: bool = False
    REFRESH_COOKIE_SAMESITE: str = "lax"

    # ── cors ──
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # ── rate limiting (in-process) ──
    AUTH_RATE_LIMIT: int = 15
    AUTH_RATE_WINDOW_SECONDS: int = 60

    # ── seed accounts ──
    SEED_ADMIN_EMAIL: str = "admin@aurelia.example"
    SEED_ADMIN_PASSWORD: str = "Detective#001"
    SEED_PLAYER_EMAIL: str = "player@aurelia.example"
    SEED_PLAYER_PASSWORD: str = "Investigate#001"

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() in {"production", "prod"}

    @property
    def refresh_cookie_path(self) -> str:
        return f"{self.API_V1_PREFIX}/auth"

    @model_validator(mode="after")
    def _ensure_secret_key(self) -> "Settings":
        if self.SECRET_KEY:
            return self
        # Reuse a previously generated key if present…
        if _SECRET_FILE.exists():
            self.SECRET_KEY = _SECRET_FILE.read_text(encoding="utf-8").strip()
            return self
        # …otherwise generate one and try to persist it.
        key = secrets.token_urlsafe(64)
        try:
            _SECRET_FILE.write_text(key, encoding="utf-8")
        except OSError:
            pass  # non-writable FS (e.g. tests): ephemeral key is fine
        self.SECRET_KEY = key
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
