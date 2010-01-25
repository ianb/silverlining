<?php
  /*
  This command is like master_runner.py, and runs at the beginning of
  every PHP request.
   */
$topp_base = "/var/www/{$_SERVER[SITE]}";
$topp_app_ini = "$topp_base/app.ini";
$topp_app_config = parse_ini_file($topp_app_ini, true);
$topp_runner = $topp_app_config['production']['runner'];

function topp_load_services() {
    global $topp_app_config;   
    foreach ($topp_app_config as $name => $value) {
        if (substr($value, 0, 8) == 'service.') {  
            $name = substr($value, 8);
            if ($name != 'php') {
                include("/var/www/support/php-services/{$name}.php");
            }
        }
    }
}
 
topp_load_services();

include("{$topp_base}/{$topp_runner}");

?>
