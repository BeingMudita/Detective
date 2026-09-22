"""End-to-end investigation flow: catalog, brief, start, discover, collect,
connect — plus fog-of-war leak checks and ownership isolation."""
from __future__ import annotations

import pytest

PREFIX = "/api/v1"


async def _auth(client, email="agent@aurelia.example"):
    res = await client.post(
        f"{PREFIX}/auth/register", json={"email": email, "password": "Investigate#001"}
    )
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


async def _start(client, headers):
    res = await client.post(f"{PREFIX}/cases/CASE-001/start", headers=headers)
    assert res.status_code == 201
    return res.json()


@pytest.mark.asyncio
async def test_catalog_lists_case_without_solution(client, imported_case):
    headers = await _auth(client)
    res = await client.get(f"{PREFIX}/cases", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert any(c["code"] == "CASE-001" for c in body)
    assert "solution" not in body[0]


@pytest.mark.asyncio
async def test_brief_exposes_initial_package_only(client, imported_case):
    headers = await _auth(client)
    res = await client.get(f"{PREFIX}/cases/CASE-001", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert "solution" not in body
    pkg = body["initial_evidence_package"]
    assert len(pkg["entities"]) == 5  # username, email, domain, ip, file
    assert {e["ext_id"] for e in pkg["evidence"]} == {"E-001", "E-002", "E-003"}


@pytest.mark.asyncio
async def test_start_reveals_only_initial_state(client, imported_case):
    headers = await _auth(client)
    data = await _start(client, headers)
    state = data["state"]
    assert len(state["entities"]) == 5
    assert state["counts"]["evidence_discovered"] == 3
    # hidden entities must not leak before discovery
    labels = {e["label"] for e in state["entities"]}
    assert "R. Vance" not in labels
    # no solution flags anywhere in the serialized entities
    for e in state["entities"]:
        assert "is_solution_actor" not in e
        assert "is_red_herring" not in e


@pytest.mark.asyncio
async def test_resume_returns_same_investigation(client, imported_case):
    headers = await _auth(client)
    first = await _start(client, headers)
    second = await _start(client, headers)
    assert second["resumed"] is True
    assert first["investigation_id"] == second["investigation_id"]


@pytest.mark.asyncio
async def test_lookup_reveals_via_pivot(client, imported_case):
    headers = await _auth(client)
    inv = (await _start(client, headers))["investigation_id"]
    res = await client.post(
        f"{PREFIX}/investigations/{inv}/lookup",
        headers=headers,
        json={"tool": "search", "query": "nightowl_42"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["hit"] is True
    revealed_labels = {e["label"] for e in body["revealed"]["entities"]}
    assert "nocturnal42" in revealed_labels
    revealed_ev = {e["ext_id"] for e in body["revealed"]["evidence"]}
    assert "E-004" in revealed_ev


@pytest.mark.asyncio
async def test_lookup_is_gated_by_prior_discovery(client, imported_case):
    headers = await _auth(client)
    inv = (await _start(client, headers))["investigation_id"]
    # aurelia-sso.example has not been discovered yet -> no leak
    res = await client.post(
        f"{PREFIX}/investigations/{inv}/lookup",
        headers=headers,
        json={"tool": "domain", "query": "aurelia-sso.example"},
    )
    assert res.status_code == 200
    assert res.json()["hit"] is False


@pytest.mark.asyncio
async def test_collect_requires_discovery(client, imported_case):
    headers = await _auth(client)
    inv = (await _start(client, headers))["investigation_id"]
    # E-020 is not discovered yet
    bad = await client.post(
        f"{PREFIX}/investigations/{inv}/evidence",
        headers=headers,
        json={"evidence_ext_id": "E-020"},
    )
    assert bad.status_code == 400

    # E-001 is an initial clue -> collectable
    ok = await client.post(
        f"{PREFIX}/investigations/{inv}/evidence",
        headers=headers,
        json={"evidence_ext_id": "E-001", "tag": "key"},
    )
    assert ok.status_code == 200
    assert ok.json()["collected"] is True


@pytest.mark.asyncio
async def test_edges_require_discovered_endpoints(client, imported_case):
    headers = await _auth(client)
    inv = (await _start(client, headers))["investigation_id"]
    ok = await client.post(
        f"{PREFIX}/investigations/{inv}/edges",
        headers=headers,
        json={"source": "e_user_nightowl", "target": "e_email_u42", "rel_type": "uses"},
    )
    assert ok.status_code == 201

    bad = await client.post(
        f"{PREFIX}/investigations/{inv}/edges",
        headers=headers,
        json={"source": "e_user_nightowl", "target": "e_emp_rosa"},
    )
    assert bad.status_code == 400  # rosa not discovered yet


@pytest.mark.asyncio
async def test_investigation_is_owner_isolated(client, imported_case):
    headers_a = await _auth(client, "a@aurelia.example")
    inv_a = (await _start(client, headers_a))["investigation_id"]

    headers_b = await _auth(client, "b@aurelia.example")
    res = await client.get(f"{PREFIX}/investigations/{inv_a}", headers=headers_b)
    assert res.status_code == 404
