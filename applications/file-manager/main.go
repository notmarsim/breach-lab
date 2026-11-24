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
		w.Write([]byte("<html><body style='font-family:system-ui;background:#f4f6f9'><header style='background:#0f172a;color:#fff;padding:1rem 2rem'><strong>Nexora File Manager</strong> (files.nexora.test)</header><main style='max-width:900px;margin:2rem auto;background:#fff;padding:1.5rem;border-radius:8px'><h2>Corporate Document Storage</h2><p>Upload, organize, and share departmental documents.</p></main></body></html>"))
	})
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	http.ListenAndServe("0.0.0.0:"+port, mux)
}
