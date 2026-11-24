<?php
if (isset($_GET['health'])) {
    header('Content-Type: application/json');
    echo json_encode(['status' => 'healthy', 'service' => 'legacy-portal', 'domain' => 'legacy.nexora.test']);
    exit;
}
?>
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Nexora Legacy Operations Portal (v1.4)</title></head>
<body bgcolor="#E8ECF0" text="#111111" style="font-family:Verdana,Arial,sans-serif;font-size:13px">
  <table width="780" align="center" border="1" cellpadding="8" cellspacing="0" bgcolor="#FFFFFF">
    <tr bgcolor="#2B4C7E"><td><font color="#FFFFFF"><b>NEXORA LEGACY OPERATIONS PORTAL v1.4 (legacy.nexora.test)</b></font></td></tr>
    <tr><td>
      <p>Legacy departmental reporting and batch lookup utility maintained for Finance &amp; Operations compatibility.</p>
    </td></tr>
  </table>
</body>
</html>
