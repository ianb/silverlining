<?
define('WP_SITEURL', rtrim("http://{$_SERVER['SILVER_CANONICAL_HOSTNAME']}{$_SERVER['SILVER_MATCH_PATH']}", "/"));
if ($_SERVER['SCRIPT_NAME'] == "/silver-update.php") {
    include("silver-update.php");
} else {
    $path = silver_call_next("{$silver_base}/wordpress/index.php");
    if ($_SERVER['REQUEST_METHOD'] == 'POST' && ! $_SERVER['SCRIPT_NAME'] != '/wp-login.php') {
        echo "I am listening\n";
    }
    include $path;
}
?>
