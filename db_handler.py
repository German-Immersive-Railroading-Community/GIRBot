import mysql.connector as sql
from decouple import config
import random as rd
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
    def add_app(self,user_id,role_id,message_id):
        appl_id = self.new_id()
        sql = "INSERT INTO Application (ID,MemberId,role,MessageID) VALUES (%s, %s, %s, %s)"
        adr=(appl_id,user_id,role_id,message_id,)
        self.cursor.execute(sql, adr)
        self.db.commit()
    def is_member(self,id):
        sql = "SELECT null FROM Member WHERE ID = %s"
        adr=(id,)
        self.cursor.execute(sql, adr)
        return len(self.cursor.fetchall())==1
    def count_app(self,id,role=None):
        sql=""
        adr=""
        if role==None:
            sql = "SELECT null FROM Application WHERE MemberID = %s"
            adr=(id,)
        else:
            sql = "SELECT null FROM Application WHERE MemberID = %s AND role = %s"
            adr=(id,role,)
        self.cursor.execute(sql, adr)
        return len(self.cursor.fetchall())
    def new_id(self):
        for i in range(100):
            #Create new id with checksum%8==0
            appl_id= rd.randint(100,999)
            qs = sum(int(digit) for digit in str(appl_id))
            checkd = 8-qs%8
            appl_id = appl_id*10+checkd
            #check if id already exist
            sql = "SELECT null FROM Application WHERE ID = %s"
            adr=(appl_id,)
            self.cursor.execute(sql, adr)
            if len(self.cursor.fetchall())==0:
                return appl_id
        raise Exception("No free application Id found")
if __name__ == "__main__":
    print("This File is not supposed to be the main file")
    exit()
