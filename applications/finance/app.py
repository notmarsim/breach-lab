"""Nexora Financial System (finance.nexora.test) — Simulated internal ledger."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Nexora Financial System")
DATA_PATH = Path(os.environ.get("NEXORA_DATASET_PATH", "/data/dataset.json"))


def _load_invoices() -> list[dict]:
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text(encoding="utf-8")).get("invoices", [])
    return []


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "finance", "domain": "finance.nexora.test"})


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    invs = _load_invoices()
    total_vol = sum(i.get("amount", 0) for i in invs)
    rows = "".join(
        f"<tr><td><strong>{html.escape(i['id'])}</strong></td><td>{html.escape(i['customer_id'])}</td>"
        f"<td>${i['amount']:.2f} {html.escape(i.get('currency','USD'))}</td>"
        f"<td><span class='badge'>{html.escape(i['status'])}</span></td></tr>"
        for i in invs
    ) or "<tr><td colspan='4'>No ledger records.</td></tr>"
    return HTMLResponse(
        f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Nexora Finance</title>
        <style>
          body {{ font-family: 'Inter', system-ui, sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }}
          header {{ background: #0f172a; color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; }}
          main {{ max-width: 1020px; margin: 2rem auto; padding: 0 1.25rem; }}
          .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.35rem; margin-bottom: 1.25rem; }}
          .badge {{ background: #dcfce7; color: #166534; padding: 2px 9px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
          table {{ width: 100%; border-collapse: collapse; }}
          th, td {{ text-align: left; padding: 0.7rem; border-bottom: 1px solid #e2e8f0; }}
        </style></head>
        <body>
          <header><div><strong style="color:#38bdf8">Nexora</strong> Financial Ledger</div><small>finance.nexora.test (Simulated)</small></header>
          <main>
            <div class="card"><h3>Total Ledger Volume: ${total_vol:,.2f} USD</h3><p style="color:#64748b;margin:0">Internal corporate invoicing and approval tracking.</p></div>
            <div class="card"><table><thead><tr><th>Invoice</th><th>Customer</th><th>Amount</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>
          </main>
        </body></html>"""
    )


@app.get("/api/invoices")
def invoices() -> dict:
    return {"invoices": _load_invoices()}
