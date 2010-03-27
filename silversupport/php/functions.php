<?

function silver_next_path($default=NULL, $url_path=NULL) {
    if (! $url_path) {
        $url_path = $_SERVER['SCRIPT_NAME'];
    }
    $path = "{$silver_base}/{$silver_php_root}/{$url_path}";
    if (is_dir($path)) {
        $path = $path . '/index.php';
    }
    if (! file_exists($path)) {
        if ($default) {
            $path = $default;
        } else {
            return NULL;
        }
    }
    return $path;
}

function silver_call_next($default=NULL, $url_path=NULL) {
    $path = silver_next_path($default, $url_path);
    if ($path) {
        chdir(dirname($path));
    }
    $_SERVER['PHP_SELF'] = $path;
    return $path;
}

?>