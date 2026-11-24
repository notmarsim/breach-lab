"""Nexora Helpdesk (support.nexora.test)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Nexora Helpdesk")
DATA_PATH = Path(os.environ.get("NEXORA_DATASET_PATH", "/data/dataset.json"))
RUNTIME_TICKETS: list[dict] = []


class TicketCreate(BaseModel):
    customer_id: str
    subject: str
    priority: str = "medium"
    category: str = "general"


def _load_tickets() -> list[dict]:
    base = []
    if DATA_PATH.exists():
        base = json.loads(DATA_PATH.read_text(encoding="utf-8")).get("tickets", [])
    return base + RUNTIME_TICKETS


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "helpdesk", "domain": "support.nexora.test"})


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(
        "<html><body style='font-family:system-ui;background:#f4f6f9'>"
        "<header style='background:#0f172a;color:#fff;padding:1rem 2rem'><strong>Nexora Helpdesk</strong> (support.nexora.test)</header>"
        "<main style='max-width:900px;margin:2rem auto;background:#fff;padding:1.5rem;border-radius:8px'>"
        "<h2>Support Portal &amp; Knowledge Base</h2><p>Open, track, and resolve enterprise support tickets.</p>"
        "</main></body></html>"
    )


@app.get("/api/tickets")
def list_tickets(q: str = "") -> dict:
    items = _load_tickets()
    if q:
        ql = q.lower()
        items = [t for t in items if ql in t["subject"].lower()]
    return {"tickets": items}


@app.post("/api/tickets", status_code=201)
def create_ticket(payload: TicketCreate) -> dict:
    if payload.priority not in ("low", "medium", "high"):
        raise HTTPException(status_code=400, detail="Invalid priority")
    ticket = {
        "id": f"TCK-RT-{len(RUNTIME_TICKETS) + 1}",
        "customer_id": payload.customer_id,
        "subject": payload.subject,
        "priority": payload.priority,
        "category": payload.category,
        "status": "open",
    }
    RUNTIME_TICKETS.append(ticket)
    return {"ticket": ticket}
