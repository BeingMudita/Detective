"""End-to-end auth flow tests against the ASGI app (SQLite-backed)."""
from __future__ import annotations

import pytest

PREFIX = "/api/v1"


async def _register(client, email="sleuth@aurelia.example", password="Investigate#001"):
    return await client.post(
        f"{PREFIX}/auth/register",
        json={"email": email, "password": password, "display_name": "Sleuth"},
    )


@pytest.mark.asyncio
async def test_health_ok(client):
    res = await client.get(f"{PREFIX}/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["database"] is True


@pytest.mark.asyncio
async def test_register_returns_token_and_user(client):
    res = await _register(client)
    assert res.status_code == 201
    body = res.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "sleuth@aurelia.example"
    assert body["user"]["role"] == "PLAYER"
    assert "password" not in body["user"]
    # httpOnly refresh cookie set
    assert client.cookies.get("id_refresh")


@pytest.mark.asyncio
async def test_register_duplicate_email_conflicts(client):
    await _register(client)
    res = await _register(client)
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password_rejected(client):
    res = await client.post(
        f"{PREFIX}/auth/register",
        json={"email": "weak@aurelia.example", "password": "onlyletters"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_login_success_and_failure(client):
    await _register(client)
    ok = await client.post(
        f"{PREFIX}/auth/login",
        json={"email": "sleuth@aurelia.example", "password": "Investigate#001"},
    )
    assert ok.status_code == 200
    assert ok.json()["access_token"]

    bad = await client.post(
        f"{PREFIX}/auth/login",
        json={"email": "sleuth@aurelia.example", "password": "nope#123"},
    )
    assert bad.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_token(client):
    res = await client.get(f"{PREFIX}/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_me_with_token(client):
    token = (await _register(client)).json()["access_token"]
    res = await client.get(f"{PREFIX}/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "sleuth@aurelia.example"


@pytest.mark.asyncio
async def test_refresh_rotates_and_logout_revokes(client):
    await _register(client)  # sets refresh cookie on the client

    first = await client.post(f"{PREFIX}/auth/refresh")
    assert first.status_code == 200
    assert first.json()["access_token"]

    # old token was rotated; the new cookie still works
    second = await client.post(f"{PREFIX}/auth/refresh")
    assert second.status_code == 200

    logout = await client.post(f"{PREFIX}/auth/logout")
    assert logout.status_code == 200

    after = await client.post(f"{PREFIX}/auth/refresh")
    assert after.status_code == 401
