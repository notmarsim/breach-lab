<?php
if (isset($_GET['health'])) {
    header('Content-Type: application/json');
    echo json_encode(['status' => 'healthy', 'service' => 'intranet', 'domain' => 'intranet.nexora.test']);
    exit;
}
$datasetPath = getenv('NEXORA_DATASET_PATH') ?: '/data/dataset.json';
$data = file_exists($datasetPath) ? json_decode(file_get_contents($datasetPath), true) : ['announcements' => []];
?>
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Nexora Intranet</title></head>
<body style="font-family:system-ui,sans-serif;background:#f4f6f9;margin:0">
  <header style="background:#0f172a;color:#fff;padding:1rem 2rem"><strong>Nexora Internal Intranet</strong> (intranet.nexora.test)</header>
  <main style="max-width:960px;margin:2rem auto;background:#fff;padding:1.5rem;border-radius:8px">
    <h2>Internal Announcements &amp; Departmental Workflows</h2>
    <?php foreach (($data['announcements'] ?? []) as $ann): ?>
      <div style="border-bottom:1px solid #e2e8f0;padding:.75rem 0">
        <h3><?= htmlspecialchars($ann['title'], ENT_QUOTES, 'UTF-8') ?></h3>
        <small><?= htmlspecialchars($ann['department'], ENT_QUOTES, 'UTF-8') ?></small>
        <p><?= htmlspecialchars($ann['summary'], ENT_QUOTES, 'UTF-8') ?></p>
      </div>
    <?php endforeach; ?>
  </main>
</body>
</html>
