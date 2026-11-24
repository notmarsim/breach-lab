"""Nexora Internal Webmail (mail.nexora.test) — strictly internal nexora.test only."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="Nexora Webmail")
DATA_PATH = Path(os.environ.get("NEXORA_DATASET_PATH", "/data/dataset.json"))
SENT_MAILS: list[dict] = []


class SendMailRequest(BaseModel):
    sender: str
    recipient: str
    subject: str
    body: str


def _all_messages() -> list[dict]:
    base = []
    if DATA_PATH.exists():
        base = json.loads(DATA_PATH.read_text(encoding="utf-8")).get("emails", [])
    return base + SENT_MAILS


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "webmail", "domain": "mail.nexora.test"})


@app.get("/", response_class=HTMLResponse)
def index(error: str = "") -> HTMLResponse:
    msgs = _all_messages()
    rows = "".join(
        f"<div style='border-bottom:1px solid #e2e8f0;padding:0.85rem 0'>"
        f"<div style='display:flex;justify-content:space-between'><strong>{html.escape(m['subject'])}</strong>"
        f"<span class='badge'>{html.escape(m.get('folder','inbox'))}</span></div>"
        f"<small style='color:#64748b'>From: {html.escape(m['from'])} &rarr; To: {html.escape(m['to'])}</small>"
        f"<p style='margin:6px 0 0;color:#334155'>{html.escape(m['body'])}</p></div>"
        for m in msgs
    )
    err_box = f"<div style='background:#fee2e2;color:#991b1b;padding:10px;border-radius:6px;margin-bottom:10px'>{html.escape(error)}</div>" if error else ""
    return HTMLResponse(
        f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Nexora Webmail</title>
        <style>
          body {{ font-family: 'Inter', system-ui, sans-serif; margin: 0; background: #f1f5f9; color: #0f172a; }}
          header {{ background: #0f172a; color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; }}
          main {{ max-width: 1040px; margin: 2rem auto; padding: 0 1.25rem; display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.5rem; }}
          .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.35rem; }}
          .badge {{ background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; }}
          input, textarea, button {{ width: 100%; padding: 8px 10px; margin: 4px 0 10px; border: 1px solid #cbd5e1; border-radius: 7px; box-sizing: border-box; }}
          button {{ background: #0ea5e9; color: #fff; border: none; font-weight: 600; cursor: pointer; }}
        </style></head>
        <body>
          <header><div><strong style="color:#38bdf8">Nexora</strong> Webmail</div><small>mail.nexora.test (@nexora.test only)</small></header>
          <main>
            <div class="card"><h2 style="margin-top:0">Mailbox</h2>{rows}</div>
            <div class="card">
              <h3 style="margin-top:0">Compose Internal Message</h3>{err_box}
              <form method="post" action="/web/send">
                <label>From</label><input name="sender" value="alice.silva@nexora.test" required>
                <label>To (@nexora.test)</label><input name="recipient" placeholder="user@nexora.test" required>
                <label>Subject</label><input name="subject" required>
                <label>Body</label><textarea name="body" rows="4" required></textarea>
                <button type="submit">Send Internal Mail</button>
              </form>
            </div>
          </main>
        </body></html>"""
    )


@app.post("/web/send")
def web_send(sender: str = Form(...), recipient: str = Form(...), subject: str = Form(...), body: str = Form(...)) -> RedirectResponse:
    if not recipient.lower().endswith("@nexora.test"):
        return RedirectResponse("/?error=External+email+delivery+is+disabled", status_code=303)
    SENT_MAILS.append(
        {"id": f"MAIL-RT-{len(SENT_MAILS) + 1}", "from": sender, "to": recipient, "subject": subject, "body": body, "folder": "sent"}
    )
    return RedirectResponse("/", status_code=303)


@app.get("/api/messages")
def list_messages() -> dict:
    return {"messages": _all_messages()}


@app.post("/api/messages", status_code=201)
def send_internal_mail(req: SendMailRequest) -> dict:
    if not req.recipient.lower().endswith("@nexora.test"):
        raise HTTPException(status_code=403, detail="External email delivery is disabled.")
    msg = {
        "id": f"MAIL-RT-{len(SENT_MAILS) + 1}",
        "from": req.sender,
        "to": req.recipient,
        "subject": req.subject,
        "body": req.body,
        "folder": "sent",
    }
    SENT_MAILS.append(msg)
    return {"message": msg}
