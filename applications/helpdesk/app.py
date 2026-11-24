"""Nexora Helpdesk (support.nexora.test)."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
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
def index(q: str = Query(default="")) -> HTMLResponse:
    tickets = _load_tickets()
    if q.strip():
        ql = q.strip().lower()
        tickets = [t for t in tickets if ql in t["subject"].lower() or ql in t["id"].lower()]

    rows = "".join(
        f"<tr><td><strong>{html.escape(t['id'])}</strong></td><td>{html.escape(t['subject'])}</td>"
        f"<td><span class='badge {html.escape(t['priority'])}'>{html.escape(t['priority'])}</span></td>"
        f"<td><span class='badge'>{html.escape(t['status'])}</span></td></tr>"
        for t in tickets
    ) or "<tr><td colspan='4'>No tickets found.</td></tr>"

    return HTMLResponse(
        f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Nexora Helpdesk</title>
        <style>
          body {{ font-family: 'Inter', system-ui, sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }}
          header {{ background: #0f172a; color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; }}
          main {{ max-width: 1080px; margin: 2rem auto; padding: 0 1.25rem; display: grid; grid-template-columns: 1.7fr 1fr; gap: 1.5rem; }}
          .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.35rem; }}
          .badge {{ padding: 3px 9px; border-radius: 999px; font-size: 12px; font-weight: 600; background: #e0f2fe; color: #0369a1; }}
          .badge.high {{ background: #fee2e2; color: #991b1b; }}
          .badge.medium {{ background: #fef3c7; color: #92400e; }}
          .badge.low {{ background: #dcfce7; color: #166534; }}
          table {{ width: 100%; border-collapse: collapse; }}
          th, td {{ text-align: left; padding: 0.65rem; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
          input, select, button {{ width: 100%; padding: 8px 10px; margin: 4px 0 10px; border: 1px solid #cbd5e1; border-radius: 7px; box-sizing: border-box; }}
          button {{ background: #0ea5e9; color: #fff; border: none; font-weight: 600; cursor: pointer; }}
        </style></head>
        <body>
          <header><div><strong style="color:#38bdf8">Nexora</strong> Helpdesk &amp; Knowledge Base</div><small>support.nexora.test</small></header>
          <main>
            <div class="card">
              <h2 style="margin-top:0">Active Support Queue</h2>
              <form method="get" style="display:flex;gap:8px;margin-bottom:10px">
                <input name="q" value="{html.escape(q)}" placeholder="Search tickets..." style="margin:0;flex:1">
                <button type="submit" style="width:auto;margin:0;padding:8px 16px">Filter</button>
              </form>
              <table><thead><tr><th>ID</th><th>Subject</th><th>Priority</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table>
            </div>
            <div>
              <div class="card">
                <h3 style="margin-top:0">Open New Ticket</h3>
                <form method="post" action="/tickets/web">
                  <label>Customer ID</label><input name="customer_id" value="CUST-2001" required>
                  <label>Subject</label><input name="subject" placeholder="Describe your issue..." required>
                  <label>Priority</label><select name="priority"><option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option></select>
                  <button type="submit">Submit Ticket</button>
                </form>
              </div>
              <div class="card" style="margin-top:1rem">
                <h4 style="margin-top:0">Knowledge Base</h4>
                <ul style="padding-left:18px;font-size:14px;color:#475569">
                  <li>KB-104: Configuring Sentinel Gateway Syslog</li>
                  <li>KB-209: Rotating Enterprise API Bearer Tokens</li>
                  <li>KB-312: Internal Mail Relay Policy (@nexora.test)</li>
                </ul>
              </div>
            </div>
          </main>
        </body></html>"""
    )


@app.post("/tickets/web")
def create_ticket_web(customer_id: str = Form(...), subject: str = Form(...), priority: str = Form("medium")) -> RedirectResponse:
    RUNTIME_TICKETS.append(
        {"id": f"TCK-RT-{len(RUNTIME_TICKETS) + 1}", "customer_id": customer_id, "subject": subject, "priority": priority, "status": "open"}
    )
    return RedirectResponse("/", status_code=303)


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
