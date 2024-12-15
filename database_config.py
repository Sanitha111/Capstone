import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',         # Database server (keep 'localhost' for local server)
        user='root',              # Your MySQL username
        password='sana anitha@1234',  # Your MySQL password
        database='train_booking'      # Your database name
    )
