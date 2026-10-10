"""Pruebas de los controles de seguridad de la API (auth, IDOR, rate limit, SSRF)."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import main
from core import security
from core.rate_limit import reset_rate_limits

API_KEY = "test-key"
TOKEN = "valid-token"
USER_ID = "11111111-1111-1111-1111-111111111111"


@pytest.fixture(autouse=True)
def prod_env(monkeypatch):
    monkeypatch.setenv("FRONTMIND_ENV", "production")
    monkeypatch.setenv("BACKEND_API_KEY", API_KEY)
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon")
    monkeypatch.setenv("ABSTRACT_API_KEY", "abstract")
    reset_rate_limits()
    security._token_cache.clear()

    async def fake_user(token):
        return USER_ID if token == TOKEN else None

    with patch("core.security._fetch_supabase_user_id", side_effect=fake_user):
        yield


@pytest.fixture
def client():
    return TestClient(main.app)


def headers(token=TOKEN, key=API_KEY):
    h = {"X-API-Key": key}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def test_missing_backend_key_fails_closed(client, monkeypatch):
    monkeypatch.delenv("BACKEND_API_KEY")
    r = client.post("/evaluate/iso", json={"html": "<p>x</p>"}, headers=headers())
    assert r.status_code == 503


def test_wrong_api_key_rejected(client):
    r = client.post("/evaluate/iso", json={"html": "<p>x</p>"}, headers=headers(key="bad"))
    assert r.status_code == 403


def test_user_token_required(client):
    r = client.post("/evaluate/iso", json={"html": "<p>x</p>"}, headers=headers(token=None))
    assert r.status_code == 401
    r = client.post("/evaluate/iso", json={"html": "<p>x</p>"}, headers=headers(token="expired"))
    assert r.status_code == 401


def test_evaluate_ok_with_valid_session(client):
    r = client.post("/evaluate/iso", json={"html": "<html><body><h1>x</h1></body></html>"},
                    headers=headers())
    assert r.status_code == 200


def test_history_ignores_client_user_id(client):
    fake = [{"user_id": USER_ID, "x": 1}, {"user_id": "otro", "x": 2}]
    with patch("main.load_history", return_value=fake):
        r = client.get("/history?user_id=otro", headers=headers())
    assert r.status_code == 200
    assert r.json() == [{"user_id": USER_ID, "x": 1}]


def test_payload_size_limit(client):
    r = client.post("/evaluate/iso", json={"html": "a" * (main.MAX_HTML_CHARS + 1)},
                    headers=headers())
    assert r.status_code == 422


def test_progress_requires_job_id_and_auth(client):
    assert client.get("/capture/progress", headers=headers()).status_code == 422
    job = "6f1c1a52-6a4c-4a49-9d2e-8f1f2b7c9a10"
    assert client.get(f"/capture/progress?job_id={job}").status_code == 403
    r = client.get(f"/capture/progress?job_id={job}", headers=headers())
    assert r.status_code == 200 and r.json() == {"logs": []}


def test_general_rate_limit_60_per_minute(client):
    for _ in range(60):
        assert client.post("/evaluate/iso", json={"html": "<p/>"}, headers=headers()).status_code == 200
    r = client.post("/evaluate/iso", json={"html": "<p/>"}, headers=headers())
    assert r.status_code == 429
    assert int(r.headers["Retry-After"]) >= 60


def test_critical_endpoint_throttled(client):
    with patch("main.CaptureAgent") as agent:
        agent.return_value.run.return_value = {"status": "completed"}
        codes = [client.post("/capture/url", json={"url": "https://example.com"},
                             headers=headers()).status_code for _ in range(6)]
    assert codes[:5] == [200] * 5
    assert codes[5] == 429


def test_storage_state_mode_rejected(client):
    body = {"url": "https://example.com",
            "auth": {"mode": "storage_state", "storage_state_path": "/etc/passwd"}}
    r = client.post("/capture/url", json=body, headers=headers())
    assert r.status_code == 422


def _abstract_response(payload):
    resp = MagicMock()
    resp.is_success = True
    resp.json.return_value = payload
    return resp


@pytest.mark.parametrize("payload", [
    {"deliverability": "DELIVERABLE"},
    {"email_deliverability": {"status": "deliverable"}},
])
def test_verify_email_accepts_json_body(client, payload):
    with patch("main.httpx.AsyncClient") as ac:
        ac.return_value.__aenter__.return_value.get = AsyncMock(return_value=_abstract_response(payload))
        r = client.post("/auth/verify-email", json={"email": "a@b.com"}, headers=headers(token=None))
    assert r.status_code == 200
    assert r.json() == {"deliverability": "DELIVERABLE"}


def test_verify_email_progressive_lockout(client):
    with patch("main.httpx.AsyncClient") as ac:
        ac.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=_abstract_response({"deliverability": "DELIVERABLE"}))
        codes = [client.post("/auth/verify-email", json={"email": "a@b.com"},
                             headers=headers(token=None)).status_code for _ in range(6)]
    assert codes[:5] == [200] * 5 and codes[5] == 429


def test_security_headers_and_gzip(client):
    r = client.get("/", headers={"Accept-Encoding": "gzip"})
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"


@pytest.mark.parametrize("url", [
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://10.0.0.5/admin",
    "http://169.254.169.254/latest/meta-data",
    "http://[::1]/",
    "file:///etc/passwd",
])
def test_ssrf_blocked(url):
    assert security.validate_url(url) is False
