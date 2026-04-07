from constants import USER_SCHEMA
from database import get_connection


conn = get_connection()
cursor = conn.cursor()
cursor.execute(USER_SCHEMA)
conn.commit()

with open("script.sql", "r") as f:
    sql = f.read()

cursor.executescript(sql)
conn.commit()
conn.close()

print("User data imported successfully!")
