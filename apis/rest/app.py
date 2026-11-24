"""Nexora Versioned REST API (api.nexora.test)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="Nexora Enterprise REST API", version="3.0.0")
DATA_PATH = Path(os.environ.get("NEXORA_DATASET_PATH", "/data/dataset.json"))
API_TOKEN = os.environ.get("NEXORA_API_TOKEN", "nexora-dev-token-v3")


def _load_dataset() -> dict:
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return {
        "employees": [{"id": "EMP-1001", "username": "alice.silva", "full_name": "Alice Silva", "email": "alice.silva@nexora.test", "department": "IT"}],
        "products": [{"sku": "NX-SEC-100", "name": "Nexora Sentinel Gateway", "price": 1299.0}],
    }


def _require_bearer(authorization: str = Header(default="")) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid API token")
    return token


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "api-rest", "versions": ["v1", "v2", "v3", "beta", "legacy"]})


@app.get("/api/v1/products")
def v1_products() -> dict:
    return {"version": "v1", "products": _load_dataset().get("products", [])}


@app.get("/api/v2/departments")
def v2_departments() -> dict:
    return {"version": "v2", "departments": _load_dataset().get("departments", [])}


@app.get("/api/v3/employees")
def v3_employees(_token: str = Depends(_require_bearer)) -> dict:
    """Protected v3 endpoint requiring valid Bearer token."""
    emps = [
        {"id": e["id"], "full_name": e["full_name"], "department": e["department"]}
        for e in _load_dataset().get("employees", [])
    ]
    return {"version": "v3", "employees": emps}


@app.get("/api/beta/status")
def beta_status() -> dict:
    return {"version": "beta", "telemetry": "nominal"}


@app.get("/api/legacy/info")
def legacy_info() -> dict:
    return {"version": "legacy", "deprecated": True, "replacement": "/api/v3/"}
