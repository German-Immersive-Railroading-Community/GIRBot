import mysql.connector as sql
from decouple import config

# Connecting and setting up SQL
class Db_interface:

    def __init__(self):
        self.db = sql.connect(
            host=str(config("host")),
            user=str(config("db_user")),
            password=str(config("db_password")),
            database=str(config("db_name"))
            )
        self.cursor = self.db.cursor()
    def status(self):
        self.cursor.execute("SHOW TABLES")
        return self.cursor.fetchall()

if __name__ == "__main__":
    db_int=Db_interface()
    print(db_int.status())
    exit()
