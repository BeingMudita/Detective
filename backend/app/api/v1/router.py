"""Aggregate all v1 routers."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import admin, auth, cases, health, investigations, meta, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(cases.router)
api_router.include_router(investigations.router)
api_router.include_router(meta.router)
api_router.include_router(admin.router)
