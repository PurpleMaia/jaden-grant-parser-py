import importlib.util
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("API_TOKEN", "token")
os.environ.setdefault("WEB_USER", "user")
os.environ.setdefault("WEB_PASS", "pass")

spec = importlib.util.spec_from_file_location("api_app", ROOT / "api_app.py")
api_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_app)
client = TestClient(api_app.app)


def test_api_requires_token(monkeypatch):
    monkeypatch.setattr(api_app, "process_grant", lambda *a, **k: {"ok": True})
    resp = client.post("/api/grant")
    assert resp.status_code in (401, 403)


def test_api_returns_json(monkeypatch, tmp_path):
    monkeypatch.setattr(api_app, "process_grant", lambda *a, **k: {"ok": True})
    headers = {"Authorization": "Bearer token"}
    files = {"files": ("f.pdf", b"data", "application/pdf")}
    resp = client.post("/api/grant", headers=headers, files=files)
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_web_requires_basic(monkeypatch):
    monkeypatch.setattr(api_app, "process_grant", lambda *a, **k: {"ok": True})
    resp = client.get("/web")
    assert resp.status_code == 401
