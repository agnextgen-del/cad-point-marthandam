# Lets Django talk to MySQL with the pure-Python PyMySQL driver
# (no C compiler needed on Windows). Skipped if mysqlclient is installed.
try:
    import pymysql
    pymysql.version_info = (2, 2, 1, "final", 0)
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
