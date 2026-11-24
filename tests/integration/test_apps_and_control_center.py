"""Integration tests for synthetic data, catalog, apps, APIs, and Control Center."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

from orchestrator.config import get_project_root
from scenario_engine.engine import ScenarioEngine
from synthetic_data.generator import generate_enterprise_dataset
from vulnerability_catalog.loader import load_catalog


def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_synthetic_data_relational_integrity() -> None:
    d1 = generate_enterprise_dataset(seed=845921)
    d2 = generate_enterprise_dataset(seed=845921)
    assert d1 == d2
    assert len(d1["departments"]) == 9
    cust_ids = {c["id"] for c in d1["customers"]}
    for order in d1["orders"]:
        assert order["customer_id"] in cust_ids
    for inv in d1["invoices"]:
        assert inv["customer_id"] in cust_ids


def test_vulnerability_catalog_loads_cleanly() -> None:
    root = get_project_root()
    modules = load_catalog(root / "vulnerability_catalog")
    assert len(modules) >= 9
    assert all(m.id and m.target_service for m in modules)


def test_scenario_engine_blackbox_hides_spoilers() -> None:
    engine = ScenarioEngine(get_project_root())
    scn = engine.compile(seed=845921, profile="balanced", mode="blackbox", difficulty="medium")
    pub = engine.public_view(scn)
    assert "services" not in pub
    assert "module_count" not in pub
    assert "authorized_scope" in pub


def test_corporate_website_endpoints() -> None:
    root = get_project_root()
    mod = _load_module_from_path("corp_app", root / "applications" / "corporate-website" / "app.py")
    client = TestClient(mod.app)
    assert client.get("/health").status_code == 200
    assert client.get("/directory?q=IT").status_code == 200


def test_webmail_blocks_external_recipients() -> None:
    root = get_project_root()
    mod = _load_module_from_path("mail_app", root / "applications" / "webmail" / "app.py")
    client = TestClient(mod.app)
    res = client.post(
        "/api/messages",
        json={
            "sender": "alice@nexora.test",
            "recipient": "external@gmail.com",
            "subject": "Test",
            "body": "Blocked",
        },
    )
    assert res.status_code == 403


def test_rest_api_v3_requires_bearer_token() -> None:
    root = get_project_root()
    mod = _load_module_from_path("rest_app", root / "apis" / "rest" / "app.py")
    client = TestClient(mod.app)
    assert client.get("/api/v1/products").status_code == 200
    assert client.get("/api/v3/employees").status_code == 401
    ok = client.get("/api/v3/employees", headers={"Authorization": "Bearer nexora-dev-token-v3"})
    assert ok.status_code == 200


def test_control_center_backend_flow() -> None:
    root = get_project_root()
    mod = _load_module_from_path("cc_app", root / "control_center" / "backend" / "app.py")
    client = TestClient(mod.app)

    assert client.get("/health").status_code == 200
    assert client.get("/api/dashboard").status_code == 200

    # Hint works in learning mode
    hint_res = client.get("/api/hints/WEB-INJ-001?level=1")
    assert hint_res.status_code == 200

    # Notes CRUD
    note_res = client.post("/api/notes", json={"title": "Recon", "content": "Checked DNS01"})
    assert note_res.status_code == 201
    assert any(n["title"] == "Recon" for n in client.get("/api/notes").json()["notes"])

    # Exam mode disables hints
    client.post("/api/scenarios/create", json={"seed": 111, "mode": "exam", "profile": "minimal", "difficulty": "easy"})
    assert client.get("/api/hints/WEB-INJ-001?level=1").status_code == 403
