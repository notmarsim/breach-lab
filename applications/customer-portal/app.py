"""Nexora Technologies Customer Portal (portal.nexora.test)."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Nexora Technologies — Customer Portal")
DATA_PATH = Path(os.environ.get("NEXORA_DATASET_PATH", "/data/dataset.json"))


def _load_dataset() -> dict:
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return {
        "customers": [{"id": "CUST-2001", "username": "alice.silva.1", "full_name": "Alice Silva", "company": "Silva Solutions Ltd.", "email": "alice@client-example.test", "tier": "enterprise"}],
        "invoices": [{"id": "INV-4001", "customer_id": "CUST-2001", "order_id": "ORD-3001", "amount": 1299.0, "currency": "USD", "status": "paid"}],
        "orders": [{"id": "ORD-3001", "customer_id": "CUST-2001", "product_name": "Nexora Sentinel Gateway", "status": "shipped"}],
    }


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "customer-portal", "domain": "portal.nexora.test"})


@app.get("/", response_class=HTMLResponse)
def portal_home(customer_id: str = Query(default="CUST-2001")) -> HTMLResponse:
    data = _load_dataset()
    customers = data.get("customers", [])
    cust = next((c for c in customers if c["id"] == customer_id), customers[0] if customers else {})
    cid = cust.get("id", "CUST-2001")
    invoices = [inv for inv in data.get("invoices", []) if inv["customer_id"] == cid]
    orders = [o for o in data.get("orders", []) if o["customer_id"] == cid]

    inv_rows = "".join(
        f"<tr><td><strong>{html.escape(i['id'])}</strong></td><td>{html.escape(i.get('order_id','-'))}</td>"
        f"<td>${i['amount']:.2f} {html.escape(i.get('currency','USD'))}</td>"
        f"<td><span class='badge {i['status']}'>{html.escape(i['status'])}</span></td></tr>"
        for i in invoices
    ) or "<tr><td colspan='4'>No invoices found.</td></tr>"

    options = "".join(
        f"<option value='{html.escape(c['id'])}' {'selected' if c['id']==cid else ''}>{html.escape(c['full_name'])} ({html.escape(c['company'])})</option>"
        for c in customers
    )

    return HTMLResponse(
        f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Nexora Customer Portal</title>
        <style>
          body {{ font-family: 'Inter', system-ui, sans-serif; margin: 0; background: #f1f5f9; color: #0f172a; }}
          header {{ background: #0f172a; color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
          main {{ max-width: 1040px; margin: 2rem auto; padding: 0 1.25rem; }}
          .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 1.25rem; }}
          .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.35rem; margin-bottom: 1.25rem; }}
          .badge {{ padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; background: #e0f2fe; color: #0369a1; }}
          .badge.paid {{ background: #dcfce7; color: #166534; }}
          .badge.pending {{ background: #fef3c7; color: #92400e; }}
          table {{ width: 100%; border-collapse: collapse; }}
          th, td {{ text-align: left; padding: 0.7rem; border-bottom: 1px solid #e2e8f0; }}
          select, button {{ padding: 0.45rem 0.75rem; border-radius: 6px; border: 1px solid #cbd5e1; }}
          button {{ background: #0ea5e9; color: #fff; border: none; font-weight: 600; cursor: pointer; }}
        </style></head>
        <body>
          <header>
            <div><strong style="color:#38bdf8">Nexora</strong> Customer Portal <small style="color:#94a3b8">(portal.nexora.test)</small></div>
            <form method="get" style="display:flex;gap:8px;align-items:center">
              <select name="customer_id">{options}</select>
              <button type="submit">Switch Account</button>
            </form>
          </header>
          <main>
            <div class="grid">
              <div class="card"><small style="color:#64748b">Account Holder</small><h3 style="margin:4px 0">{html.escape(cust.get('full_name','N/A'))}</h3><div>{html.escape(cust.get('company',''))}</div></div>
              <div class="card"><small style="color:#64748b">Subscription Tier</small><h3 style="margin:4px 0;text-transform:uppercase">{html.escape(cust.get('tier','standard'))}</h3><span class="badge">Active</span></div>
              <div class="card"><small style="color:#64748b">Orders &amp; Devices</small><h3 style="margin:4px 0">{len(orders)}</h3><div>Active entitlements</div></div>
            </div>
            <div class="card">
              <h3 style="margin-top:0">Invoices &amp; Payment History</h3>
              <table><thead><tr><th>Invoice</th><th>Order Ref</th><th>Amount</th><th>Status</th></tr></thead><tbody>{inv_rows}</tbody></table>
            </div>
            <div class="card">
              <h3 style="margin-top:0">Security &amp; Active Sessions</h3>
              <p style="color:#475569;margin-bottom:0.5rem">Current Session: <code>web-session-{html.escape(cid.lower())}</code> (TLS Terminated at DMZ Proxy)</p>
              <span class="badge">MFA Policy: Optional</span>
            </div>
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
