"""Nexora Technologies Corporate Website (www.nexora.test)."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from pathlib import Path

from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

app = FastAPI(title="Nexora Technologies — Corporate Website")

DATA_PATH = Path(os.environ.get("NEXORA_DATASET_PATH", "/data/dataset.json"))
DB_PATH = Path(os.environ.get("CORPORATE_DB_PATH", str(Path(tempfile.gettempdir()) / "corporate.db")))

BASE_STYLE = """
<style>
  body { font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; background: #f4f6f9; color: #1e293b; }
  header { background: #0f172a; color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
  header a { color: #cbd5e1; text-decoration: none; margin-left: 1.2rem; font-size: 0.95rem; }
  header a:hover { color: #fff; }
  .brand { font-weight: 700; font-size: 1.25rem; color: #38bdf8; }
  main { max-width: 1080px; margin: 2rem auto; padding: 0 1.25rem; }
  .card { background: #fff; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }
  input, textarea, select { width: 100%; padding: 0.55rem; margin: 0.35rem 0 0.8rem; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
  button { background: #0284c7; color: #fff; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; cursor: pointer; font-weight: 600; }
  button:hover { background: #0369a1; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: 0.65rem; border-bottom: 1px solid #e2e8f0; }
  footer { text-align: center; padding: 2rem; color: #64748b; font-size: 0.85rem; }
</style>
"""


def _load_dataset() -> dict:
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return {
        "departments": [{"id": "it", "name": "Information Technology", "code": "IT"}],
        "employees": [{"id": "EMP-1001", "full_name": "Alice Silva", "department": "Information Technology", "title": "IT Lead", "email": "alice.silva@nexora.test"}],
        "announcements": [{"id": "ANN-01", "title": "Nexora Sentinel 4.2 Released", "department": "Engineering", "summary": "Enterprise telemetry update available."}],
    }


def _init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, message TEXT)"
    )
    conn.commit()
    conn.close()


_init_db()


def _render_page(title: str, body: str) -> HTMLResponse:
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} — Nexora Technologies</title>{BASE_STYLE}</head>
<body>
<header>
  <span class="brand">Nexora Technologies</span>
  <nav>
    <a href="/">Home</a>
    <a href="/news">News</a>
    <a href="/departments">Departments</a>
    <a href="/directory">Directory</a>
    <a href="/careers">Careers</a>
    <a href="/documents">Documents</a>
    <a href="/contact">Contact</a>
    <a href="/admin">Admin</a>
  </nav>
</header>
<main>{body}</main>
<footer>&copy; 2026 Nexora Technologies (nexora.test) — Enterprise Security &amp; Telemetry</footer>
</body></html>"""
    return HTMLResponse(html)


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "corporate-website", "domain": "www.nexora.test"})


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return _render_page(
        "Home",
        """
        <div class="card">
          <h1>Enterprise Security &amp; Resilient Infrastructure</h1>
          <p>Nexora Technologies delivers telemetry, identity governance, and defensive engineering solutions for modern enterprises.</p>
        </div>
        <div class="grid">
          <div class="card"><h3>Sentinel Gateway</h3><p>Segmented perimeter inspection and traffic visibility.</p></div>
          <div class="card"><h3>Identity Vault</h3><p>Centralized workforce authentication and access governance.</p></div>
          <div class="card"><h3>AuditStream</h3><p>High-throughput compliance and security event logging.</p></div>
        </div>
        """,
    )


@app.get("/news", response_class=HTMLResponse)
def news() -> HTMLResponse:
    data = _load_dataset()
    items = "".join(
        f"<div class='card'><h3>{a['title']}</h3><small>{a['department']}</small><p>{a['summary']}</p></div>"
        for a in data.get("announcements", [])
    )
    return _render_page("News", f"<h2>Corporate News</h2>{items}")


@app.get("/departments", response_class=HTMLResponse)
def departments() -> HTMLResponse:
    data = _load_dataset()
    cards = "".join(
        f"<div class='card'><h3>{d['name']}</h3><p>Code: <code>{d['code']}</code></p></div>"
        for d in data.get("departments", [])
    )
    return _render_page("Departments", f"<h2>Departments</h2><div class='grid'>{cards}</div>")


@app.get("/directory", response_class=HTMLResponse)
def directory(q: str = Query(default="")) -> HTMLResponse:
    data = _load_dataset()
    emps = data.get("employees", [])
    if q.strip():
        ql = q.strip().lower()
        emps = [e for e in emps if ql in e["full_name"].lower() or ql in e["department"].lower()]
    rows = "".join(
        f"<tr><td>{e['full_name']}</td><td>{e['title']}</td><td>{e['department']}</td><td>{e['email']}</td></tr>"
        for e in emps
    )
    body = f"""
    <div class="card">
      <h2>Public Employee Directory</h2>
      <form method="get"><input type="text" name="q" value="{q}" placeholder="Search by name or department..."><button type="submit">Search</button></form>
      <table><thead><tr><th>Name</th><th>Title</th><th>Department</th><th>Email</th></tr></thead><tbody>{rows}</tbody></table>
    </div>
    """
    return _render_page("Directory", body)


@app.get("/careers", response_class=HTMLResponse)
def careers() -> HTMLResponse:
    return _render_page(
        "Careers",
        """
        <div class="card"><h2>Open Positions</h2>
        <ul>
          <li><strong>Senior Linux Systems Engineer</strong> — Operations (Remote / Hybrid)</li>
          <li><strong>Backend Security Engineer</strong> — Engineering</li>
          <li><strong>Technical Support Specialist</strong> — Customer Support</li>
        </ul></div>
        """,
    )


@app.get("/documents", response_class=HTMLResponse)
def documents() -> HTMLResponse:
    return _render_page(
        "Public Documents",
        """
        <div class="card"><h2>Public Documentation</h2>
        <ul>
          <li>Nexora Enterprise Architecture Overview (2026-Q1)</li>
          <li>Nexora Acceptable Use &amp; Vendor Security Policy</li>
          <li>Customer Onboarding Guide v3.4</li>
        </ul></div>
        """,
    )


@app.get("/contact", response_class=HTMLResponse)
def contact_form(sent: int = 0) -> HTMLResponse:
    notice = "<p style='color:#059669;'><strong>Thank you!</strong> Your message has been recorded.</p>" if sent else ""
    return _render_page(
        "Contact",
        f"""
        <div class="card"><h2>Contact Nexora</h2>{notice}
        <form method="post" action="/contact">
          <label>Name</label><input type="text" name="name" required>
          <label>Email</label><input type="email" name="email" required>
          <label>Message</label><textarea name="message" rows="4" required></textarea>
          <button type="submit">Send Message</button>
        </form></div>
        """,
    )


@app.post("/contact")
def contact_submit(name: str = Form(...), email: str = Form(...), message: str = Form(...)) -> RedirectResponse:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)", (name, email, message))
    conn.commit()
    conn.close()
    return RedirectResponse("/contact?sent=1", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin_area() -> HTMLResponse:
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    conn.close()
    return _render_page(
        "Admin",
        f"<div class='card'><h2>Corporate CMS Administration</h2><p>Recorded contact submissions: <strong>{count}</strong></p></div>",
    )
