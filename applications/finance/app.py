"""Nexora Financial System (finance.nexora.test) — Simulated internal ledger."""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Nexora Financial System")
DATA_PATH = Path(os.environ.get("NEXORA_DATASET_PATH", "/data/dataset.json"))


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "finance", "domain": "finance.nexora.test"})


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(
        "<html><body style='font-family:system-ui;background:#f4f6f9'>"
        "<header style='background:#0f172a;color:#fff;padding:1rem 2rem'><strong>Nexora Finance</strong> (finance.nexora.test)</header>"
        "<main style='max-width:900px;margin:2rem auto;background:#fff;padding:1.5rem;border-radius:8px'>"
        "<h2>Internal Accounts, Invoices &amp; Approvals</h2><p>Simulated corporate financial ledger.</p>"
        "</main></body></html>"
    )


@app.get("/api/invoices")
def invoices() -> dict:
    if DATA_PATH.exists():
        return {"invoices": json.loads(DATA_PATH.read_text(encoding="utf-8")).get("invoices", [])}
    return {"invoices": []}
