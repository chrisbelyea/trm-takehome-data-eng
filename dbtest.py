import os

import psycopg2

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT", "5432")

dbcon = psycopg2.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
cursor = dbcon.cursor()
cursor.execute("SELECT VERSION()")
data = cursor.fetchone()
print(data)
dbcon.close()
