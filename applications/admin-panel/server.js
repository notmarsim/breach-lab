const express = require("express");
const app = express();
app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({ status: "healthy", service: "admin-panel", domain: "admin.nexora.test" });
});

app.get("/", (_req, res) => {
  res.send(
    "<html><body style='font-family:system-ui;background:#f4f6f9'>" +
      "<header style='background:#0f172a;color:#fff;padding:1rem 2rem'><strong>Nexora Administration Panel</strong> (admin.nexora.test)</header>" +
      "<main style='max-width:900px;margin:2rem auto;background:#fff;padding:1.5rem;border-radius:8px'>" +
      "<h2>Directory, Groups &amp; Corporate Settings</h2><p>Internal corporate administration interface.</p>" +
      "</main></body></html>"
  );
});

app.listen(process.env.PORT || 3001, "0.0.0.0");
