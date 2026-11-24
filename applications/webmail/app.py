"""Nexora Internal Webmail (mail.nexora.test) — strictly internal nexora.test only."""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Nexora Webmail")
DATA_PATH = Path(os.environ.get("NEXORA_DATASET_PATH", "/data/dataset.json"))
SENT_MAILS: list[dict] = []


class SendMailRequest(BaseModel):
    sender: str
    recipient: str
    subject: str
    body: str


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "webmail", "domain": "mail.nexora.test"})


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(
        "<html><body style='font-family:system-ui;background:#f4f6f9'>"
        "<header style='background:#0f172a;color:#fff;padding:1rem 2rem'><strong>Nexora Webmail</strong> (mail.nexora.test)</header>"
        "<main style='max-width:900px;margin:2rem auto;background:#fff;padding:1.5rem;border-radius:8px'>"
        "<h2>Internal Corporate Messaging</h2><p>Restricted to @nexora.test addresses.</p>"
        "</main></body></html>"
    )


@app.get("/api/messages")
def list_messages() -> dict:
    base = []
    if DATA_PATH.exists():
        base = json.loads(DATA_PATH.read_text(encoding="utf-8")).get("emails", [])
    return {"messages": base + SENT_MAILS}


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
