# Optional pure-Python MySQL driver used when DB_ENGINE=mysql.
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
