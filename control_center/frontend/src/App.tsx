import React, { useEffect, useState } from "react";

type Tab = "dashboard" | "scenarios" | "discovery" | "resources" | "recovery" | "notes" | "settings";

interface DashboardData {
  lab_status: string;
  scenario: {
    scenario_id: string;
    profile: string;
    mode: string;
    difficulty: string;
    domain: string;
  };
  host_resources: {
    total_ram_mb: number;
    available_ram_mb: number;
    cpu_count: number;
    free_disk_gb: number;
  };
  progress: {
    completed: number;
    total_in_scenario: number | null;
  };
}

export default function App() {
  const [tab, setTab] = useState<Tab>("dashboard");
  const [dash, setDash] = useState<DashboardData | null>(null);
  const [flagModule, setFlagModule] = useState("");
  const [flagValue, setFlagValue] = useState("");
  const [flagMsg, setFlagMsg] = useState("");
  const [noteTitle, setNoteTitle] = useState("");
  const [noteContent, setNoteContent] = useState("");
  const [notes, setNotes] = useState<Array<{ id: number; title: string; content: string }>>([]);

  useEffect(() => {
    fetch("/api/dashboard")
      .then((r) => r.json())
      .then(setDash)
      .catch(() => setDash(null));
    fetch("/api/notes")
      .then((r) => r.json())
      .then((d) => setNotes(d.notes || []))
      .catch(() => setNotes([]));
  }, []);

  async function submitFlag(e: React.FormEvent) {
    e.preventDefault();
    const res = await fetch("/api/discovery/submit-flag", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ module_id: flagModule, flag: flagValue }),
    });
    const data = await res.json();
    setFlagMsg(data.accepted ? `Accepted: ${data.module_id}` : data.detail || data.message || "Rejected");
  }

  async function saveNote(e: React.FormEvent) {
    e.preventDefault();
    await fetch("/api/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: noteTitle, content: noteContent }),
    });
    setNoteTitle("");
    setNoteContent("");
    const updated = await fetch("/api/notes").then((r) => r.json());
    setNotes(updated.notes || []);
  }

  const tabs: Array<{ id: Tab; label: string }> = [
    { id: "dashboard", label: "Dashboard" },
    { id: "scenarios", label: "Scenario Manager" },
    { id: "discovery", label: "Discovery Center" },
    { id: "resources", label: "Resource Manager" },
    { id: "recovery", label: "Recovery Center" },
    { id: "notes", label: "Personal Notes" },
    { id: "settings", label: "Settings" },
  ];

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <aside style={{ width: 220, background: "#020617", padding: "1.5rem 1rem", borderRight: "1px solid #1e293b" }}>
        <h2 style={{ color: "#38bdf8", marginTop: 0 }}>BreachLab</h2>
        <p style={{ fontSize: 12, color: "#94a3b8" }}>Control Center (Isolated)</p>
        <nav style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              style={{
                textAlign: "left",
                padding: "0.6rem 0.8rem",
                background: tab === t.id ? "#0284c7" : "transparent",
                color: "#e2e8f0",
                border: "none",
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </aside>
      <main style={{ flex: 1, padding: "2rem" }}>
        {tab === "dashboard" && (
          <section>
            <h1>Lab Dashboard</h1>
            {dash ? (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 16 }}>
                <div style={{ background: "#1e293b", padding: 16, borderRadius: 8 }}>
                  <h3>Active Scenario</h3>
                  <p>{dash.scenario.scenario_id}</p>
                  <small>{dash.scenario.profile} | {dash.scenario.mode} | {dash.scenario.difficulty}</small>
                </div>
                <div style={{ background: "#1e293b", padding: 16, borderRadius: 8 }}>
                  <h3>Host Resources</h3>
                  <p>{dash.host_resources.available_ram_mb} / {dash.host_resources.total_ram_mb} MB RAM</p>
                  <small>{dash.host_resources.cpu_count} CPUs | {dash.host_resources.free_disk_gb} GB free</small>
                </div>
                <div style={{ background: "#1e293b", padding: 16, borderRadius: 8 }}>
                  <h3>Progress</h3>
                  <p>{dash.progress.completed} completed</p>
                </div>
              </div>
            ) : (
              <p>Connect to Control Center API on port 8443.</p>
            )}
          </section>
        )}
        {tab === "discovery" && (
          <section>
            <h1>Discovery Center</h1>
            <form onSubmit={submitFlag} style={{ display: "flex", flexDirection: "column", gap: 8, maxWidth: 400 }}>
              <input placeholder="Module ID (e.g. WEB-INJ-001)" value={flagModule} onChange={(e) => setFlagModule(e.target.value)} />
              <input placeholder="Flag Token (BL{...})" value={flagValue} onChange={(e) => setFlagValue(e.target.value)} />
              <button type="submit">Submit Flag</button>
            </form>
            {flagMsg && <p>{flagMsg}</p>}
          </section>
        )}
        {tab === "notes" && (
          <section>
            <h1>Personal Notes (Markdown)</h1>
            <form onSubmit={saveNote} style={{ display: "flex", flexDirection: "column", gap: 8, maxWidth: 500 }}>
              <input placeholder="Title" value={noteTitle} onChange={(e) => setNoteTitle(e.target.value)} required />
              <textarea rows={4} placeholder="Markdown notes..." value={noteContent} onChange={(e) => setNoteContent(e.target.value)} required />
              <button type="submit">Save Note</button>
            </form>
            <div style={{ marginTop: 20 }}>
              {notes.map((n) => (
                <div key={n.id} style={{ background: "#1e293b", padding: 12, borderRadius: 8, marginBottom: 8 }}>
                  <strong>{n.title}</strong>
                  <pre style={{ whiteSpace: "pre-wrap" }}>{n.content}</pre>
                </div>
              ))}
            </div>
          </section>
        )}
        {["scenarios", "resources", "recovery", "settings"].includes(tab) && (
          <section>
            <h1>{tabs.find((t) => t.id === tab)?.label}</h1>
            <p>Managed via Control Center API endpoints under <code>/api/</code>.</p>
          </section>
        )}
      </main>
    </div>
  );
}
