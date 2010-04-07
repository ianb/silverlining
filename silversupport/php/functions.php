<?

function silver_next_path($default=NULL, $url_path=NULL) {
    global $silver_base, $silver_php_root;
    if (! $url_path) {
        $url_path = $_SERVER['SCRIPT_NAME'];
    }
    $path = "{$silver_base}/{$silver_php_root}/{$url_path}";
    if (is_dir($path) and file_exists(rtrim($path, '/') . '/index.php')) {
        if (rtrim($path, '/') == $path) {
            # We need a redirect
            header("Status: 301 Moved Permanently");
            header("Location: {$url_path}/");
            exit();
        }
        $path = rtrim($path, '/') . '/index.php';
    }
    if (! file_exists($path)) {
        if ($default) {
            /*echo "Path '{$path}' (in '{$silver_php_root}') didn't exist<br>\n";*/
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