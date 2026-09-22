"""Case submission + debrief."""
from __future__ import annotations

import pytest

PREFIX = "/api/v1"


async def _auth(client, email="closer@aurelia.example"):
    res = await client.post(
        f"{PREFIX}/auth/register", json={"email": email, "password": "Investigate#001"}
    )
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


async def _start(client, headers):
    res = await client.post(f"{PREFIX}/cases/CASE-001/start", headers=headers)
    return res.json()["investigation_id"]


async def _discover_actor(client, headers, inv):
    # pivot: email lookup on the initial email reveals the employee (R. Vance)
    await client.post(
        f"{PREFIX}/investigations/{inv}/lookup",
        headers=headers,
        json={"tool": "email", "query": "user42@aurelia.example"},
    )


@pytest.mark.asyncio
async def test_attack_vectors_endpoint(client, imported_case):
    headers = await _auth(client)
    res = await client.get(f"{PREFIX}/meta/attack-vectors", headers=headers)
    assert res.status_code == 200
    assert "compromised_credentials" in res.json()["attack_vectors"]


@pytest.mark.asyncio
async def test_submit_correct_actor_debrief(client, imported_case):
    headers = await _auth(client)
    inv = await _start(client, headers)
    await _discover_actor(client, headers, inv)

    res = await client.post(
        f"{PREFIX}/investigations/{inv}/submit",
        headers=headers,
        json={
            "actor_ext_id": "e_emp_rosa",
            "attack_vector": "compromised_credentials",
            "cited_evidence": ["E-019"],
            "summary": "Credentials phished; used the nightowl persona from an external IP.",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["verdict"]["correct_actor"] is True
    assert body["verdict"]["correct_vector"] is True
    # solution is revealed only after submission
    assert body["solution"]["actor_label"] == "R. Vance"


@pytest.mark.asyncio
async def test_cannot_accuse_undiscovered_entity(client, imported_case):
    headers = await _auth(client)
    inv = await _start(client, headers)
    # rosa not discovered yet
    res = await client.post(
        f"{PREFIX}/investigations/{inv}/submit",
        headers=headers,
        json={"actor_ext_id": "e_emp_rosa", "attack_vector": "compromised_credentials"},
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_unknown_attack_vector_rejected(client, imported_case):
    headers = await _auth(client)
    inv = await _start(client, headers)
    await _discover_actor(client, headers, inv)
    res = await client.post(
        f"{PREFIX}/investigations/{inv}/submit",
        headers=headers,
        json={"actor_ext_id": "e_emp_rosa", "attack_vector": "alien_intervention"},
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_cannot_submit_twice(client, imported_case):
    headers = await _auth(client)
    inv = await _start(client, headers)
    await _discover_actor(client, headers, inv)
    ok = await client.post(
        f"{PREFIX}/investigations/{inv}/submit",
        headers=headers,
        json={"actor_ext_id": "e_emp_rosa", "attack_vector": "compromised_credentials"},
    )
    assert ok.status_code == 200
    again = await client.post(
        f"{PREFIX}/investigations/{inv}/submit",
        headers=headers,
        json={"actor_ext_id": "e_emp_rosa", "attack_vector": "compromised_credentials"},
    )
    assert again.status_code == 400
