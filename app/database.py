import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()  

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )

print("MYSQL_USER:", os.getenv("MYSQL_USER"))
print("MYSQL_PASSWORD:", os.getenv("MYSQL_PASSWORD"))
print("MYSQL_HOST:", os.getenv("MYSQL_HOST"))
print("MYSQL_DB:", os.getenv("MYSQL_DB"))
