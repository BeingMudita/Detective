"""Unit tests for hashing, tokens and the rate limiter (no DB, no network)."""
from __future__ import annotations

import uuid

from app.core.rate_limit import FixedWindowLimiter
from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("Investigate#001")
    assert hashed != "Investigate#001"
    assert verify_password("Investigate#001", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_verify_password_rejects_garbage_hash():
    assert verify_password("anything", "not-a-real-hash") is False


def test_access_token_roundtrip():
    uid = uuid.uuid4()
    token = create_access_token(uid, "PLAYER")
    payload = decode_access_token(token)
    assert payload["sub"] == str(uid)
    assert payload["role"] == "PLAYER"
    assert payload["type"] == "access"


def test_refresh_token_hashing_is_deterministic_and_unique():
    a = generate_refresh_token()
    b = generate_refresh_token()
    assert a != b
    assert hash_refresh_token(a) == hash_refresh_token(a)
    assert hash_refresh_token(a) != hash_refresh_token(b)
    assert len(hash_refresh_token(a)) == 64  # sha-256 hex


def test_fixed_window_limiter_blocks_after_limit():
    limiter = FixedWindowLimiter()
    key = "1.2.3.4:/login"
    assert all(limiter.allow(key, limit=3, window_seconds=60) for _ in range(3))
    assert limiter.allow(key, limit=3, window_seconds=60) is False
    limiter.reset()
    assert limiter.allow(key, limit=3, window_seconds=60) is True
