import os
import MySQLdb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

def get_db_connection():
    db_config = {
        'host': DB_HOST,
        'user': DB_USER,
        'passwd': DB_PASSWORD,
        'db': DB_NAME
    }
    conn = MySQLdb.connect(**db_config)
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    return conn, cursor

def get_table_df(table_name):
    """해당 테이블을 DataFrame으로 반환"""
    conn, cursor = get_db_connection()
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, conn)
        return df
    finally:
        cursor.close()
        conn.close()