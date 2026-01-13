import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="postgres123",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    try:
        cur.execute("CREATE DATABASE packaxis")
    except psycopg2.Error as db_err:
        if "already exists" not in str(db_err):
            raise
    cur.close()
    conn.close()
    print("Database 'packaxis' created successfully!")
except psycopg2.Error as e:
    print(f"Error: {e}")
