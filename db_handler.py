import mysql.connector as sql
from decouple import config

# Connecting and setting up SQL
db = sql.connect(
    host=str(config("host")),
    user=str(config("db_user")),
    password=str(config("db_password")),
    database=str(config("db_name"))
    )

if __name__ == "__main__":
    print("Please run main.py, not this file!")
    exit()