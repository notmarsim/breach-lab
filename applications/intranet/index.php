<?php
if (isset($_GET['health'])) {
    header('Content-Type: application/json');
    echo json_encode(['status' => 'healthy', 'service' => 'intranet', 'domain' => 'intranet.nexora.test']);
    exit;
}
$datasetPath = getenv('NEXORA_DATASET_PATH') ?: '/data/dataset.json';
$data = file_exists($datasetPath) ? json_decode(file_get_contents($datasetPath), true) : ['announcements' => [], 'employees' => []];
$q = trim($_GET['q'] ?? '');
$employees = $data['employees'] ?? [];
if ($q !== '') {
    $employees = array_filter($employees, fn($e) => stripos($e['full_name'], $q) !== false || stripos($e['department'], $q) !== false);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Nexora Internal Intranet</title>
  <style>
    body { font-family: 'Inter', system-ui, sans-serif; margin: 0; background: #f1f5f9; color: #0f172a; }
    header { background: #0f172a; color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
    main { max-width: 1080px; margin: 2rem auto; padding: 0 1.25rem; display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.5rem; }
    .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.35rem; margin-bottom: 1.25rem; }
    .badge { background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 0.6rem; border-bottom: 1px solid #e2e8f0; font-size: 13.5px; }
    input, button { padding: 8px 10px; border-radius: 6px; border: 1px solid #cbd5e1; }
    button { background: #0ea5e9; color: #fff; border: none; font-weight: 600; cursor: pointer; }
  </style>
</head>
<body>
  <header><div><strong style="color:#38bdf8">Nexora</strong> Corporate Intranet</div><small>intranet.nexora.test — Internal Only</small></header>
  <main>
    <div>
      <div class="card">
        <h2 style="margin-top:0">Internal Announcements</h2>
        <?php foreach (($data['announcements'] ?? []) as $ann): ?>
          <div style="border-bottom:1px solid #e2e8f0;padding:.75rem 0">
            <span class="badge"><?= htmlspecialchars($ann['department'], ENT_QUOTES, 'UTF-8') ?></span>
            <h3 style="margin:.4rem 0 .2rem"><?= htmlspecialchars($ann['title'], ENT_QUOTES, 'UTF-8') ?></h3>
            <p style="margin:0;color:#475569"><?= htmlspecialchars($ann['summary'], ENT_QUOTES, 'UTF-8') ?></p>
          </div>
        <?php endforeach; ?>
      </div>
      <div class="card">
        <h2 style="margin-top:0">Internal Staff Directory</h2>
        <form method="get" style="display:flex;gap:8px;margin-bottom:10px">
          <input name="q" value="<?= htmlspecialchars($q, ENT_QUOTES, 'UTF-8') ?>" placeholder="Search staff or department..." style="flex:1">
          <button type="submit">Search</button>
        </form>
        <table><thead><tr><th>Name</th><th>Title</th><th>Department</th></tr></thead><tbody>
          <?php foreach (array_slice($employees, 0, 10) as $emp): ?>
            <tr>
              <td><strong><?= htmlspecialchars($emp['full_name'], ENT_QUOTES, 'UTF-8') ?></strong></td>
              <td><?= htmlspecialchars($emp['title'], ENT_QUOTES, 'UTF-8') ?></td>
              <td><span class="badge"><?= htmlspecialchars($emp['department'], ENT_QUOTES, 'UTF-8') ?></span></td>
            </tr>
          <?php endforeach; ?>
        </tbody></table>
      </div>
    </div>
    <div>
      <div class="card">
        <h3 style="margin-top:0">Corporate Calendar</h3>
        <ul style="padding-left:18px;font-size:14px;color:#475569">
          <li><strong>Nov 28</strong> — Quarterly Security Audit Sync</li>
          <li><strong>Dec 03</strong> — Infrastructure Backup Verification</li>
          <li><strong>Dec 12</strong> — Engineering All-Hands</li>
        </ul>
      </div>
      <div class="card">
        <h3 style="margin-top:0">Departmental Resources</h3>
        <p style="font-size:14px;color:#475569">Access internal mail at <code>mail.nexora.test</code> and support queues at <code>support.nexora.test</code>.</p>
      </div>
    </div>
  </main>
</body>
</html>
