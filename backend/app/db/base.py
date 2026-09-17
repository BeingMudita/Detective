"""Declarative base. Models use portable column types (Uuid, JSON) so the same
schema runs on PostgreSQL (production) and SQLite (tests) unchanged."""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
