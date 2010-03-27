<?php
  /*
  This command is like master-runner.py, and runs at the beginning of
  every PHP request.
   */

if ($_SERVER['SILVER_SCRIPT_NAME']) {
    $_SERVER['SCRIPT_NAME'] = $_SERVER['SILVER_SCRIPT_NAME'];
}

if ($_SERVER['SILVER_INSTANCE_DIR']) {
    $silver_base = $_SERVER['SILVER_INSTANCE_DIR'];
} else {
    $silver_base = "/var/www/{$_SERVER[SILVER_INSTANCE_NAME]}";
}
if (! $_SERVER['SILVER_CANONICAL_HOSTNAME']) {
    $_SERVER['SILVER_CANONICAL_HOSTNAME'] = $_SERVER['HTTP_HOST'];
}

$silver_app_ini = "$silver_base/app.ini";
$silver_app_config = parse_ini_file($silver_app_ini, true);
$silver_runner = $silver_app_config['production']['runner'];
$silver_php_root = $silver_app_config['production']['php_root'];

define('SILVER_SECRET', file_get_contents('/var/lib/silverlining/secret.txt'));

require_once "/usr/local/share/silverlining/lib/silversupport/php/functions.php";
include "{$silver_base}/silver-env-variables.php";
include "{$silver_base}/{$silver_runner}";

?>