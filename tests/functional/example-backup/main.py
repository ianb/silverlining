import MySQLdb
import os
import time
import traceback


def application(environ, start_response):
    try:
        import sys
        print >> sys.stderr, dict(host=os.environ['CONFIG_MYSQL_HOST'] or '127.0.0.1',
                               user=os.environ['CONFIG_MYSQL_USER'],
                               passwd=os.environ['CONFIG_MYSQL_PASSWORD'],
                               db=os.environ['CONFIG_MYSQL_DBNAME'],
                               port=int(os.environ['CONFIG_MYSQL_PORT'])
                               if os.environ['CONFIG_MYSQL_PORT'] else None)
        kw = {}
        if os.environ['CONFIG_MYSQL_HOST']:
            kw['host'] = os.environ['CONFIG_MYSQL_HOST']
        if os.environ['CONFIG_MYSQL_PORT']:
            kw['port'] = int(os.environ['CONFIG_MYSQL_PORT'])
        if os.environ['CONFIG_MYSQL_PASSWORD']:
            kw['passwd'] = os.environ['CONFIG_MYSQL_PASSWORD']
        conn = MySQLdb.connect(user=os.environ['CONFIG_MYSQL_USER'],
                               db=os.environ['CONFIG_MYSQL_DBNAME'],
                               **kw)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
          id INT PRIMARY KEY AUTO_INCREMENT,
          name TEXT,
          value TEXT
        );
        """)
        cur.execute("""
        INSERT INTO test_table (name, value) VALUES (%s, %s)
        """, ('time_run', str(time.time())))
        start_response('200 OK', [('content-type', 'text/plain')])
        return ['Inserted']
    except:
        start_response('500 Server Error', [('content-type', 'text/plain')])
        return [traceback.format_exc()]
