"""Nexora Technologies Customer Portal (portal.nexora.test)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Nexora Technologies — Customer Portal")
DATA_PATH = Path(os.environ.get("NEXORA_DATASET_PATH", "/data/dataset.json"))


def _load_dataset() -> dict:
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return {
        "customers": [{"id": "CUST-2001", "username": "alice.silva.1", "full_name": "Alice Silva", "tier": "enterprise"}],
        "invoices": [{"id": "INV-4001", "customer_id": "CUST-2001", "amount": 1299.0, "status": "paid"}],
    }


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "customer-portal", "domain": "portal.nexora.test"})


@app.get("/", response_class=HTMLResponse)
def portal_home() -> HTMLResponse:
    return HTMLResponse(
        """<!DOCTYPE html><html><head><meta charset="utf-8"><title>Nexora Customer Portal</title></head>
        <body style="font-family:system-ui,sans-serif;background:#f4f6f9;margin:0">
          <header style="background:#0f172a;color:#fff;padding:1rem 2rem"><strong>Nexora Customer Portal</strong> (portal.nexora.test)</header>
          <main style="max-width:960px;margin:2rem auto;padding:1.5rem;background:#fff;border-radius:8px">
            <h2>Account, Subscriptions &amp; Billing</h2>
            <p>Manage your Nexora subscriptions, invoices, security preferences, and active sessions.</p>
          </main>
        </body></html>"""
    )


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str) -> dict:
    data = _load_dataset()
    cust = next((c for c in data.get("customers", []) if c["id"] == customer_id), None)
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    invoices = [inv for inv in data.get("invoices", []) if inv["customer_id"] == customer_id]
    return {"customer": cust, "invoices": invoices}
