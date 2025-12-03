
import mariadb
def get_db_connection():
    """
    Create and return a MariaDB connection.
    Update host/user/password/database to match your environment.
    """
    conn = mariadb.connect(
        host="localhost",
        port=3306,
        user="root",
        password="",
        database="pcc_accounting",
    )
    return conn

