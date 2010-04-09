<?
function table_exists ($table, $db) {
    $tables = mysql_list_tables ($db);
    while (list ($temp) = mysql_fetch_array ($tables)) {
        if ($temp == $table) {
            return TRUE;
        }
    }
    return FALSE;
}

$password = $_SERVER['CONFIG_MYSQL_PASSWORD'];
if (! $password) {
    $password = null;
}

//echo "mysql_connect({$_SERVER[CONFIG_MYSQL_HOST]}, {$_SERVER[CONFIG_MYSQL_USER]}, {$password});";

mysql_connect($_SERVER['CONFIG_MYSQL_HOST'], $_SERVER['CONFIG_MYSQL_USER'],
                    $password);
//mysql_select_db($_SERVER[CONFIG_MYSQL_DBNAME], $db);

if (! table_exists("wp_posts", $_SERVER['CONFIG_MYSQL_DBNAME'])) {
    define('WP_INSTALLING', TRUE);
    /** Load WordPress Bootstrap */
    require_once(dirname(__FILE__) . '/wordpress/wp-load.php');
    /** Load WordPress Administration Upgrade API */
    require_once(dirname(__FILE__) . '/wordpress/wp-admin/includes/upgrade.php');
    /* FIXME: hardcoding example email address, and Public=True */
    echo "Setting up tables and basic information; admin information needed...\n";
    echo "Admin user (default: admin): ";
    flush();
    $handle = fopen("php://stdin", "r");
    $username = trim(fgets(STDIN));
    if (! $username) {
        $username = 'admin';
    }
    echo "Email: ";
    flush();
    $email = trim(fgets(STDIN));
    $result = wp_install('Just Another Blog', $username, $email, TRUE);
    echo "Blog created:\n";
    echo "  username: {$username}\n";
    echo "  password: {$result['password']}\n";
    echo "Installed.\n";
} else {
    echo "Database already available.\n";
}

?>