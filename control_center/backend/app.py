"""BreachLab Control Center Backend (FastAPI + SQLite).

Strictly separated from vulnerable targets. Never exposes Docker socket or
unsubmitted flags to the frontend.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from orchestrator.config import get_project_root, list_profiles
from orchestrator.recovery_manager import RecoveryManager
from orchestrator.resource_manager import ResourceManager
from scenario_engine.engine import ScenarioEngine
from vulnerability_catalog.loader import load_catalog

app = FastAPI(title="BreachLab Control Center API", version="0.1.0")

ROOT = get_project_root()
DB_PATH = Path(os.environ.get("BREACHLAB_CC_DB", str(ROOT / ".breachlab" / "control_center.db")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    conn = _conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS progress (
            module_id TEXT PRIMARY KEY,
            completed_at TEXT NOT NULL,
            method TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS hint_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id TEXT NOT NULL,
            level INTEGER NOT NULL,
            requested_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            session_id TEXT NOT NULL DEFAULT 'default',
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )
    conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('training_mode', 'learning')")
    conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('spoiler_protection', 'true')")
    conn.commit()
    conn.close()


_init_db()

# Active compiled scenario cache (in-memory for current session)
_ENGINE = ScenarioEngine(ROOT)
_ACTIVE_SCENARIO = _ENGINE.compile(seed=845921, profile="balanced", mode="learning", difficulty="medium")


class FlagSubmission(BaseModel):
    module_id: str
    flag: str


class ScenarioCreateRequest(BaseModel):
    seed: int = 845921
    profile: str = "balanced"
    mode: str = "learning"
    difficulty: str = "medium"


class NotePayload(BaseModel):
    title: str
    content: str
    session_id: str = "default"


class SettingUpdate(BaseModel):
    key: str
    value: str


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "control-center-backend"})


@app.get("/api/dashboard")
def dashboard() -> dict:
    rm = ResourceManager(ROOT)
    host = rm.get_host_resources()
    conn = _conn()
    completed_count = conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0]
    conn.close()
    return {
        "lab_status": "ready",
        "scenario": _ENGINE.public_view(_ACTIVE_SCENARIO),
        "host_resources": {
            "total_ram_mb": host.total_ram_mb,
            "available_ram_mb": host.available_ram_mb,
            "cpu_count": host.cpu_count,
            "free_disk_gb": host.free_disk_gb,
        },
        "progress": {
            "completed": completed_count,
            "total_in_scenario": len(_ACTIVE_SCENARIO.modules) if _ACTIVE_SCENARIO.mode != "blackbox" else None,
        },
    }


@app.get("/api/scenarios/active")
def get_active_scenario() -> dict:
    return _ENGINE.public_view(_ACTIVE_SCENARIO)


@app.post("/api/scenarios/create")
def create_scenario(req: ScenarioCreateRequest) -> dict:
    global _ACTIVE_SCENARIO
    try:
        _ACTIVE_SCENARIO = _ENGINE.compile(
            seed=req.seed,
            profile=req.profile,
            mode=req.mode,
            difficulty=req.difficulty,
        )
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _ENGINE.public_view(_ACTIVE_SCENARIO)


@app.get("/api/resources/profiles")
def get_profiles() -> dict:
    rm = ResourceManager(ROOT)
    return {
        "profiles": list_profiles(ROOT),
        "recommended": rm.recommend_profile(),
    }


@app.post("/api/discovery/submit-flag")
def submit_flag(payload: FlagSubmission) -> dict:
    expected = _ACTIVE_SCENARIO.flags.get(payload.module_id)
    if not expected:
        raise HTTPException(status_code=404, detail="Unknown module_id in active scenario.")
    if payload.flag.strip() != expected:
        return {"accepted": False, "message": "Invalid flag token."}

    now = datetime.now(timezone.utc).isoformat()
    conn = _conn()
    conn.execute(
        "INSERT OR IGNORE INTO progress (module_id, completed_at, method) VALUES (?, ?, 'flag')",
        (payload.module_id, now),
    )
    conn.commit()
    conn.close()
    return {"accepted": True, "module_id": payload.module_id, "completed_at": now}


@app.get("/api/discovery/progress")
def get_progress() -> dict:
    conn = _conn()
    rows = conn.execute("SELECT module_id, completed_at, method FROM progress ORDER BY completed_at DESC").fetchall()
    conn.close()
    return {"completed": [dict(r) for r in rows]}


@app.get("/api/hints/{module_id}")
def get_hint(module_id: str, level: int = Query(1, ge=1, le=4)) -> dict:
    if _ACTIVE_SCENARIO.mode == "exam":
        raise HTTPException(status_code=403, detail="Hints are disabled in Exam mode.")
    catalog = {m.id: m for m in load_catalog(ROOT / "vulnerability_catalog")}
    mod = catalog.get(module_id)
    if not mod:
        raise HTTPException(status_code=404, detail="Module not found.")
    if level > len(mod.hints):
        raise HTTPException(status_code=404, detail="Requested hint level not available.")

    conn = _conn()
    conn.execute(
        "INSERT INTO hint_usage (module_id, level, requested_at) VALUES (?, ?, ?)",
        (module_id, level, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return {"module_id": module_id, "level": level, "hint": mod.hints[level - 1]}


@app.get("/api/notes")
def list_notes(q: Optional[str] = None) -> dict:
    conn = _conn()
    if q:
        rows = conn.execute(
            "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY updated_at DESC",
            (f"%{q}%", f"%{q}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM notes ORDER BY updated_at DESC").fetchall()
    conn.close()
    return {"notes": [dict(r) for r in rows]}


@app.post("/api/notes", status_code=201)
def create_note(payload: NotePayload) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    conn = _conn()
    cur = conn.execute(
        "INSERT INTO notes (title, content, session_id, updated_at) VALUES (?, ?, ?, ?)",
        (payload.title, payload.content, payload.session_id, now),
    )
    conn.commit()
    note_id = cur.lastrowid
    conn.close()
    return {"id": note_id, "title": payload.title, "updated_at": now}


@app.get("/api/recovery/snapshots")
def list_snapshots() -> dict:
    rm = RecoveryManager(ROOT)
    return {
        "snapshots": [
            {"name": s.name, "created_at": s.created_at, "includes_progress": s.includes_progress}
            for s in rm.list_snapshots()
        ]
    }


@app.post("/api/recovery/snapshots")
def create_snapshot(name: Optional[str] = None) -> dict:
    rm = RecoveryManager(ROOT)
    try:
        snap = rm.create_snapshot(name=name)
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"name": snap.name, "created_at": snap.created_at}


@app.get("/api/settings")
def get_settings() -> dict:
    conn = _conn()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {"settings": {r["key"]: r["value"] for r in rows}}


@app.put("/api/settings")
def update_setting(payload: SettingUpdate) -> dict:
    conn = _conn()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (payload.key, payload.value),
    )
    conn.commit()
    conn.close()
    return {"updated": True, "key": payload.key, "value": payload.value}
