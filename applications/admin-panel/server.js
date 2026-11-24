const express = require("express");
const app = express();
app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({ status: "healthy", service: "admin-panel", domain: "admin.nexora.test" });
});

app.get("/", (_req, res) => {
  res.send(`<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Nexora Administration Panel</title>
  <style>
    body { font-family: 'Inter', system-ui, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }
    header { background: #020617; padding: 1rem 2rem; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; }
    main { max-width: 1020px; margin: 2rem auto; padding: 0 1.25rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.25rem; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 1.25rem; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 0.65rem; border-bottom: 1px solid #334155; }
    .badge { background: #0284c7; color: #fff; padding: 2px 8px; border-radius: 999px; font-size: 12px; }
  </style></head>
  <body>
    <header><div><strong style="color:#38bdf8">Nexora</strong> IAM &amp; Systems Admin</div><small>admin.nexora.test (Restricted)</small></header>
    <main>
      <div class="grid">
        <div class="card"><small>Directory Users</small><h2 style="margin:6px 0">18</h2></div>
        <div class="card"><small>Security Groups</small><h2 style="margin:6px 0">9</h2></div>
        <div class="card"><small>Service Health</small><h2 style="margin:6px 0;color:#4ade80">Nominal</h2></div>
      </div>
      <div class="card">
        <h3 style="margin-top:0">Recent Audit Log</h3>
        <table><thead><tr><th>Event</th><th>Actor</th><th>Target</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td>ROLE_SYNC</td><td>iam-daemon</td><td>Engineering</td><td><span class="badge">OK</span></td></tr>
          <tr><td>BACKUP_ROTATE</td><td>backup01</td><td>/srv/backups</td><td><span class="badge">OK</span></td></tr>
        </tbody></table>
      </div>
    </main>
  </body></html>`);
});

app.listen(process.env.PORT || 3001, "0.0.0.0");
