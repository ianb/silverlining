<?php
  /*
  This command is like master_runner.py, and runs at the beginning of
  every PHP request.
   */
$silver_base = "/var/www/{$_SERVER[SILVER_INSTANCE_NAME]}";
$silver_app_ini = "$silver_base/app.ini";
$silver_app_config = parse_ini_file($silver_app_ini, true);
$silver_runner = $silver_app_config['production']['runner'];

function silver_load_services() {
    global $silver_app_config;   
    foreach ($silver_app_config as $name => $value) {
        if (substr($value, 0, 8) == 'service.') {  
            $name = substr($value, 8);
            if ($name != 'php') {
                include("/usr/local/share/silverlining/lib/silversupport/php-services/{$name}.php");
            }
        }
    }
}
 
silver_load_services();

include("{$silver_base}/{$silver_runner}");

?>
