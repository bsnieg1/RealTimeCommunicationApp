import uuid

import httpx2
import pytest

BASE_URL = "http://127.0.0.1:8000"


def _register_and_login(username: str) -> str:
    password = "supersecret123"
    httpx2.post(
        f"{BASE_URL}/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )
    resp = httpx2.post(f"{BASE_URL}/auth/login", json={"identifier": username, "password": password})
    return resp.json()["access_token"]


@pytest.fixture
def token1() -> str:
    return _register_and_login(f"wstest1_{uuid.uuid4().hex[:8]}")


@pytest.fixture
def token2() -> str:
    return _register_and_login(f"wstest2_{uuid.uuid4().hex[:8]}")


@pytest.fixture
def channel_id(token1: str, token2: str) -> int:
    resp = httpx2.post(
        f"{BASE_URL}/channels",
        json={"name": f"wstest-{uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    cid = resp.json()["id"]

    httpx2.post(f"{BASE_URL}/channels/{cid}/join", headers={"Authorization": f"Bearer {token2}"})

    return cid
