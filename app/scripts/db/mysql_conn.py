import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="database",
            user="admin",
            password="admin7791",
            database="lab_test"
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"MySQL Error: {e}")
        return None

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        conn.close()
