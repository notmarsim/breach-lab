package main

import (
	"encoding/json"
	"net/http"
	"os"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{
			"status":  "healthy",
			"service": "file-manager",
			"domain":  "files.nexora.test",
		})
	})
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write([]byte(`<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Nexora File Manager</title>
<style>
  body { font-family: 'Inter', system-ui, sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }
  header { background: #0f172a; color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; }
  main { max-width: 980px; margin: 2rem auto; padding: 0 1.25rem; }
  .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.35rem; margin-bottom: 1.25rem; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: 0.7rem; border-bottom: 1px solid #e2e8f0; }
  .badge { background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; }
</style></head>
<body>
  <header><div><strong style="color:#38bdf8">Nexora</strong> Corporate Drive</div><small>files.nexora.test</small></header>
  <main>
    <div class="card"><h3>Storage Quota: 14.2 GB / 100 GB used</h3><p style="color:#64748b;margin:0">Departmental file shares and versioned corporate documents.</p></div>
    <div class="card">
      <table><thead><tr><th>Name</th><th>Department</th><th>Size</th><th>Access</th></tr></thead>
      <tbody>
        <tr><td><strong>/engineering/sentinel-architecture-v4.pdf</strong></td><td>Engineering</td><td>4.2 MB</td><td><span class="badge">Internal</span></td></tr>
        <tr><td><strong>/finance/q4-budget-forecast.xlsx</strong></td><td>Finance</td><td>1.1 MB</td><td><span class="badge">Restricted</span></td></tr>
        <tr><td><strong>/hr/employee-handbook-2026.pdf</strong></td><td>HR</td><td>2.8 MB</td><td><span class="badge">All Staff</span></td></tr>
      </tbody></table>
    </div>
  </main>
</body></html>`))
	})
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	http.ListenAndServe("0.0.0.0:"+port, mux)
}
