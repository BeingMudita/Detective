"""Role-based access control on the admin probe route."""
from __future__ import annotations

import pytest

PREFIX = "/api/v1"


@pytest.mark.asyncio
async def test_admin_route_rejects_anonymous(client):
    res = await client.get(f"{PREFIX}/admin/ping")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_admin_route_rejects_player(client):
    reg = await client.post(
        f"{PREFIX}/auth/register",
        json={"email": "player@aurelia.example", "password": "Investigate#001"},
    )
    token = reg.json()["access_token"]
    res = await client.get(
        f"{PREFIX}/admin/ping", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_admin_route_accepts_admin(client, admin_credentials):
    login = await client.post(f"{PREFIX}/auth/login", json=admin_credentials)
    assert login.status_code == 200
    token = login.json()["access_token"]
    res = await client.get(
        f"{PREFIX}/admin/ping", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["ok"] is True
