<?php
  /*
  This command is like master-runner.py, and runs at the beginning of
  every PHP request.
   */
if ($_SERVER[SILVER_INSTANCE_DIR]) {
    $silver_base = $_SERVER[SILVER_INSTANCE_DIR];
} else {
    $silver_base = "/var/www/{$_SERVER[SILVER_INSTANCE_NAME]}";
}
$silver_app_ini = "$silver_base/app.ini";
$silver_app_config = parse_ini_file($silver_app_ini, true);
$silver_runner = $silver_app_config['production']['runner'];

define('SILVER_SECRET', file_get_contents('/var/lib/silverlining/secret.txt'));

include "{$silver_base}/silver-env-variables.php";
include "{$silver_base}/{$silver_runner}";

?>
