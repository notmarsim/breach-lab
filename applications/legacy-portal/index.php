<?php
if (isset($_GET['health'])) {
    header('Content-Type: application/json');
    echo json_encode(['status' => 'healthy', 'service' => 'legacy-portal', 'domain' => 'legacy.nexora.test']);
    exit;
}
$batch = htmlspecialchars($_GET['batch'] ?? '', ENT_QUOTES, 'UTF-8');
?>
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Nexora Legacy Operations Portal (v1.4)</title></head>
<body bgcolor="#D4DCE6" text="#111111" style="font-family:Verdana,Arial,sans-serif;font-size:12px;margin:20px">
  <table width="820" align="center" border="1" cellpadding="10" cellspacing="0" bgcolor="#FFFFFF" bordercolor="#7A8FA6">
    <tr bgcolor="#1E3A5F">
      <td><font color="#FFFFFF" size="3"><b>NEXORA LEGACY OPERATIONS PORTAL v1.4</b></font> <font color="#A8C5E5">(legacy.nexora.test)</font></td>
    </tr>
    <tr bgcolor="#EEF2F6">
      <td><b>Module:</b> Batch Invoice &amp; Warehouse Lookup | <b>Status:</b> Compatibility Mode (PHP 8.2)</td>
    </tr>
    <tr>
      <td>
        <form method="get" action="/">
          <b>Lookup Batch ID:</b>
          <input type="text" name="batch" value="<?= $batch ?>" size="24" placeholder="e.g. BATCH-2026-Q4">
          <input type="submit" value="Query">
        </form>
        <?php if ($batch !== ''): ?>
          <hr>
          <p><b>Query Result for <code><?= $batch ?></code>:</b> Archived in Finance Ledger (Status: RECONCILED).</p>
        <?php endif; ?>
        <hr>
        <font color="#555555" size="1">Internal Legacy System &copy; 2012-2026 Nexora Technologies Operations.</font>
      </td>
    </tr>
  </table>
</body>
</html>
