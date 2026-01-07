import pymysql

# Override version info to satisfy Django's mysqlclient version check
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.install_as_MySQLdb()