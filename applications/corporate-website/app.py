"""Nexora Technologies Corporate Website (www.nexora.test)."""

from __future__ import annotations

import html
import json
import os
import sqlite3
import tempfile
from pathlib import Path

from fastapi import FastAPI, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

app = FastAPI(title="Nexora Technologies — Corporate Website")

DATA_PATH = Path(os.environ.get("NEXORA_DATASET_PATH", "/data/dataset.json"))
DB_PATH = Path(os.environ.get("CORPORATE_DB_PATH", str(Path(tempfile.gettempdir()) / "corporate.db")))

CORPORATE_CSS = """
<style>
  :root {
    --navy: #0b132b; --slate: #1c2541; --accent: #0ea5e9; --accent-dark: #0284c7;
    --bg: #f8fafc; --card: #ffffff; --text: #0f172a; --muted: #64748b; --border: #e2e8f0;
  }
  * { box-sizing: border-box; }
  body { font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif; margin: 0; background: var(--bg); color: var(--text); line-height: 1.6; }
  .topbar { background: var(--navy); color: #cbd5e1; font-size: 0.8rem; padding: 0.4rem 2rem; display: flex; justify-content: space-between; border-bottom: 1px solid #1e293b; }
  header { background: var(--slate); color: #fff; padding: 0.95rem 2rem; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 20; box-shadow: 0 2px 10px rgba(0,0,0,0.15); }
  .brand { display: flex; align-items: center; gap: 0.65rem; font-weight: 700; font-size: 1.2rem; color: #fff; text-decoration: none; letter-spacing: -0.02em; }
  .brand span { color: var(--accent); }
  nav { display: flex; flex-wrap: wrap; gap: 1.15rem; align-items: center; }
  nav a { color: #e2e8f0; text-decoration: none; font-size: 0.92rem; font-weight: 500; transition: color 0.15s; }
  nav a:hover { color: var(--accent); }
  .hero { background: linear-gradient(135deg, #0b132b 0%, #1c2541 60%, #0369a1 100%); color: #fff; padding: 4rem 2rem; }
  .hero-inner { max-width: 1120px; margin: 0 auto; display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; align-items: center; }
  .hero h1 { font-size: 2.5rem; line-height: 1.15; margin: 0 0 1rem; letter-spacing: -0.03em; }
  .hero p { color: #cbd5e1; font-size: 1.08rem; margin: 0 0 1.5rem; }
  .btn { display: inline-block; background: var(--accent); color: #fff; padding: 0.7rem 1.35rem; border-radius: 8px; text-decoration: none; font-weight: 600; border: none; cursor: pointer; font-size: 0.95rem; }
  .btn:hover { background: var(--accent-dark); }
  .btn-outline { background: transparent; border: 1px solid #64748b; color: #fff; margin-left: 0.6rem; }
  .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; background: rgba(255,255,255,0.06); padding: 1.25rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.12); }
  .stat strong { display: block; font-size: 1.6rem; color: #38bdf8; }
  .stat span { font-size: 0.82rem; color: #cbd5e1; }
  main { max-width: 1120px; margin: 2.25rem auto; padding: 0 1.5rem; min-height: 60vh; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1.5rem; margin-bottom: 1.25rem; box-shadow: 0 1px 3px rgba(15,23,42,0.04); }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem; }
  .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; background: #e0f2fe; color: #0369a1; }
  input, textarea, select { width: 100%; padding: 0.65rem 0.8rem; margin: 0.35rem 0 0.9rem; border: 1px solid #cbd5e1; border-radius: 8px; font-family: inherit; font-size: 0.95rem; }
  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); padding: 0.75rem; border-bottom: 2px solid var(--border); }
  td { padding: 0.8rem 0.75rem; border-bottom: 1px solid var(--border); font-size: 0.94rem; }
  tr:hover td { background: #f8fafc; }
  .pagination { display: flex; gap: 0.5rem; margin-top: 1rem; align-items: center; }
  .pagination a { padding: 0.4rem 0.8rem; border: 1px solid var(--border); border-radius: 6px; text-decoration: none; color: var(--text); font-size: 0.88rem; }
  .pagination a.active { background: var(--accent); color: #fff; border-color: var(--accent); }
  footer { background: var(--navy); color: #94a3b8; padding: 2.5rem 2rem; margin-top: 3rem; font-size: 0.88rem; }
  .footer-inner { max-width: 1120px; margin: 0 auto; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }
  @media (max-width: 768px) { .hero-inner { grid-template-columns: 1fr; } }
</style>
"""

LOGO_SVG = """<svg width="28" height="28" viewBox="0 0 32 32" fill="none"><rect width="32" height="32" rx="8" fill="#0ea5e9"/><path d="M9 22V10l7 6 7-6v12" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>"""


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
        "CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, message TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS job_applications (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, applicant TEXT, email TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.commit()
    conn.close()


_init_db()


def _render_page(title: str, body: str, include_hero: bool = False) -> HTMLResponse:
    hero_html = ""
    if include_hero:
        hero_html = """
        <section class="hero">
          <div class="hero-inner">
            <div>
              <span class="badge" style="background:rgba(56,189,248,0.2);color:#7dd3fc;margin-bottom:0.8rem;">ENTERPRISE SECURITY PLATFORM</span>
              <h1>Resilient Infrastructure for Modern Enterprises</h1>
              <p>Nexora Technologies engineers network telemetry, identity governance, and audit automation trusted by global operations teams.</p>
              <a class="btn" href="/directory">Explore Team</a>
              <a class="btn btn-outline" href="/contact">Request Briefing</a>
            </div>
            <div class="stats">
              <div class="stat"><strong>99.98%</strong><span>Telemetry Uptime</span></div>
              <div class="stat"><strong>140+</strong><span>Enterprise Clients</span></div>
              <div class="stat"><strong>24/7</strong><span>SOC Operations</span></div>
            </div>
          </div>
        </section>"""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — Nexora Technologies</title>{CORPORATE_CSS}</head>
<body>
<div class="topbar"><span>Nexora Technologies Inc. — Corporate Portal</span><span>Domain: nexora.test | Support: support.nexora.test</span></div>
<header>
  <a class="brand" href="/">{LOGO_SVG} Nexora <span>Technologies</span></a>
  <nav>
    <a href="/">Home</a>
    <a href="/news">Newsroom</a>
    <a href="/departments">Departments</a>
    <a href="/directory">Directory</a>
    <a href="/careers">Careers</a>
    <a href="/documents">Documents</a>
    <a href="/contact">Contact</a>
    <a href="/admin">Admin</a>
  </nav>
</header>
{hero_html}
<main>{body}</main>
<footer><div class="footer-inner"><div><strong>Nexora Technologies</strong><br>Enterprise Security, Telemetry &amp; Infrastructure</div><div>&copy; 2026 Nexora Technologies (nexora.test)</div></div></footer>
</body></html>"""
    return HTMLResponse(page)


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "corporate-website", "domain": "www.nexora.test"})


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    body = """
    <div class="grid">
      <div class="card"><span class="badge">Network</span><h3>Nexora Sentinel Gateway</h3><p>Deep perimeter segmentation and automated anomaly telemetry across hybrid corporate zones.</p></div>
      <div class="card"><span class="badge">Identity</span><h3>Nexora Identity Vault</h3><p>Unified role-based access control, directory federation, and policy auditing.</p></div>
      <div class="card"><span class="badge">Compliance</span><h3>AuditStream Enterprise</h3><p>Tamper-evident operational logging and automated executive compliance reporting.</p></div>
    </div>
    <div class="card" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem">
      <div><h3 style="margin:0 0 0.3rem">Looking for Nexora hardware or licenses?</h3><p style="margin:0;color:#64748b">Visit our official enterprise store or manage active subscriptions in the Customer Portal.</p></div>
      <div><a class="btn" href="http://shop.nexora.test:8080">Enterprise Store</a></div>
    </div>
    """
    return _render_page("Home", body, include_hero=True)


@app.get("/news", response_class=HTMLResponse)
def news() -> HTMLResponse:
    data = _load_dataset()
    items = "".join(
        f"<div class='card'><span class='badge'>{html.escape(a['department'])}</span>"
        f"<h3 style='margin-top:0.6rem'>{html.escape(a['title'])}</h3>"
        f"<p style='color:#475569'>{html.escape(a['summary'])}</p></div>"
        for a in data.get("announcements", [])
    )
    return _render_page("Newsroom", f"<h2>Corporate Newsroom</h2>{items}")


@app.get("/departments", response_class=HTMLResponse)
def departments() -> HTMLResponse:
    data = _load_dataset()
    emps = data.get("employees", [])
    cards = ""
    for d in data.get("departments", []):
        count = sum(1 for e in emps if e.get("department_id") == d["id"])
        cards += (
            f"<div class='card'><span class='badge'>{html.escape(d['code'])}</span>"
            f"<h3 style='margin:0.6rem 0 0.3rem'>{html.escape(d['name'])}</h3>"
            f"<p style='color:#64748b;margin:0'>Active staff: <strong>{count}</strong></p></div>"
        )
    return _render_page("Departments", f"<h2>Corporate Departments</h2><div class='grid'>{cards}</div>")


@app.get("/directory", response_class=HTMLResponse)
def directory(q: str = Query(default=""), page: int = Query(default=1, ge=1)) -> HTMLResponse:
    data = _load_dataset()
    emps = data.get("employees", [])
    if q.strip():
        ql = q.strip().lower()
        emps = [e for e in emps if ql in e["full_name"].lower() or ql in e["department"].lower() or ql in e["title"].lower()]

    per_page = 8
    total_pages = max(1, (len(emps) + per_page - 1) // per_page)
    page = min(page, total_pages)
    slice_emps = emps[(page - 1) * per_page : page * per_page]

    rows = "".join(
        f"<tr><td><strong>{html.escape(e['full_name'])}</strong></td><td>{html.escape(e['title'])}</td>"
        f"<td><span class='badge'>{html.escape(e['department'])}</span></td>"
        f"<td><code>{html.escape(e['email'])}</code></td></tr>"
        for e in slice_emps
    ) or "<tr><td colspan='4'>No matching employees found.</td></tr>"

    pager = "".join(
        f"<a class='{'active' if p == page else ''}' href='/directory?q={html.escape(q)}&page={p}'>{p}</a>"
        for p in range(1, total_pages + 1)
    )
    body = f"""
    <div class="card">
      <h2>Public Employee Directory</h2>
      <form method="get" style="display:flex;gap:0.75rem;align-items:center;margin-bottom:1rem">
        <input type="text" name="q" value="{html.escape(q)}" placeholder="Filter by name, title, or department..." style="margin:0">
        <button class="btn" type="submit">Search</button>
      </form>
      <table><thead><tr><th>Name</th><th>Role</th><th>Department</th><th>Corporate Email</th></tr></thead><tbody>{rows}</tbody></table>
      <div class="pagination"><span style="color:#64748b;font-size:0.85rem">Page {page} of {total_pages} ({len(emps)} results)</span>{pager}</div>
    </div>
    """
    return _render_page("Employee Directory", body)


@app.get("/careers", response_class=HTMLResponse)
def careers(applied: int = 0) -> HTMLResponse:
    banner = "<div class='card' style='border-left:4px solid #10b981;background:#ecfdf5'><strong>Application received!</strong> Our HR team will review your submission.</div>" if applied else ""
    return _render_page(
        "Careers",
        f"""{banner}
        <div class="grid">
          <div class="card"><span class="badge">Operations</span><h3>Senior Linux Systems Engineer</h3><p>Manage hardened Ubuntu server fleets, network segmentation, and automated backups.</p></div>
          <div class="card"><span class="badge">Engineering</span><h3>Backend Platform Engineer</h3><p>Design resilient Python, Go, and Node.js microservices for enterprise telemetry.</p></div>
          <div class="card"><span class="badge">Support</span><h3>Enterprise Support Specialist</h3><p>Assist B2B clients with Sentinel Gateway onboarding and incident triage.</p></div>
        </div>
        <div class="card">
          <h3>Submit Application</h3>
          <form method="post" action="/careers">
            <label>Position</label>
            <select name="role"><option>Senior Linux Systems Engineer</option><option>Backend Platform Engineer</option><option>Enterprise Support Specialist</option></select>
            <label>Full Name</label><input type="text" name="applicant" required>
            <label>Email</label><input type="email" name="email" required>
            <button class="btn" type="submit">Apply Now</button>
          </form>
        </div>""",
    )


@app.post("/careers")
def careers_apply(role: str = Form(...), applicant: str = Form(...), email: str = Form(...)) -> RedirectResponse:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO job_applications (role, applicant, email) VALUES (?, ?, ?)", (role, applicant, email))
    conn.commit()
    conn.close()
    return RedirectResponse("/careers?applied=1", status_code=303)


@app.get("/documents", response_class=HTMLResponse)
def documents() -> HTMLResponse:
    return _render_page(
        "Public Documents",
        """
        <div class="card"><h2>Public Corporate Documentation</h2>
        <table>
          <thead><tr><th>Document</th><th>Category</th><th>Version</th><th>Published</th></tr></thead>
          <tbody>
            <tr><td>Nexora Enterprise Architecture Whitepaper</td><td><span class="badge">Architecture</span></td><td>v4.2</td><td>2026-09-15</td></tr>
            <tr><td>Vendor &amp; Acceptable Use Policy</td><td><span class="badge">Governance</span></td><td>v2.1</td><td>2026-08-01</td></tr>
            <tr><td>Sentinel Gateway Deployment Guide</td><td><span class="badge">Operations</span></td><td>v3.4</td><td>2026-10-10</td></tr>
          </tbody>
        </table></div>
        """,
    )


@app.get("/contact", response_class=HTMLResponse)
def contact_form(sent: int = 0) -> HTMLResponse:
    notice = "<div class='card' style='border-left:4px solid #10b981;background:#ecfdf5'><strong>Thank you!</strong> Your inquiry has been logged by our communications team.</div>" if sent else ""
    return _render_page(
        "Contact",
        f"""{notice}
        <div class="card"><h2>Contact Nexora Technologies</h2>
        <form method="post" action="/contact">
          <label>Full Name</label><input type="text" name="name" required>
          <label>Corporate Email</label><input type="email" name="email" required>
          <label>Message</label><textarea name="message" rows="4" required></textarea>
          <button class="btn" type="submit">Send Inquiry</button>
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
    contacts = conn.execute("SELECT id, name, email, created_at FROM contacts ORDER BY id DESC LIMIT 10").fetchall()
    apps = conn.execute("SELECT COUNT(*) FROM job_applications").fetchone()[0]
    conn.close()
    rows = "".join(
        f"<tr><td>#{c[0]}</td><td>{html.escape(c[1])}</td><td>{html.escape(c[2])}</td><td>{html.escape(str(c[3]))}</td></tr>"
        for c in contacts
    ) or "<tr><td colspan='4'>No contact submissions yet.</td></tr>"
    return _render_page(
        "CMS Administration",
        f"""
        <div class="grid">
          <div class="card"><h3>Contact Submissions</h3><p style="font-size:1.8rem;font-weight:700;margin:0">{len(contacts)}</p></div>
          <div class="card"><h3>Job Applications</h3><p style="font-size:1.8rem;font-weight:700;margin:0">{apps}</p></div>
        </div>
        <div class="card"><h3>Recent Inquiries</h3>
        <table><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Timestamp</th></tr></thead><tbody>{rows}</tbody></table></div>
        """,
    )
