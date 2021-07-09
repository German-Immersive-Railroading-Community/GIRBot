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

    def add_app(self, user_id, role_id, message_id):
        app_id = self.new_id()
        sql = "INSERT INTO Application (ID,MemberId,role,MessageID) VALUES (%s, %s, %s, %s)"
        adr = (app_id, user_id, role_id, message_id,)
        self.cursor.execute(sql, adr)
        self.db.commit()

    def is_member(self, id):
        sql = "SELECT null FROM Member WHERE ID = %s"
        adr = (id,)
        self.cursor.execute(sql, adr)
        return len(self.cursor.fetchall()) == 1

    def count_app(self, id, role=None):
        sql = ""
        adr = ""
        if role == None:
            sql = "SELECT null FROM Application WHERE MemberID = %s"
            adr = (id,)
        else:
            sql = "SELECT null FROM Application WHERE MemberID = %s AND role = %s"
            adr = (id, role,)
        self.cursor.execute(sql, adr)
        return len(self.cursor.fetchall())

    def new_id(self):
        for i in range(100):
            # Create new id with checksum%8==0
            app_id = rd.randint(100, 999)
            qs = sum(int(digit) for digit in str(app_id))
            checkd = 8-qs % 8
            app_id = app_id*10+checkd
            # check if id already exist
            sql = "SELECT null FROM Application WHERE ID = %s"
            adr = (app_id,)
            self.cursor.execute(sql, adr)
            if len(self.cursor.fetchall()) == 0:
                return app_id
        raise Exception("No free application Id found")

    def check_vote(self,app_id):
        sql = "SELECT is_in_favor FROM app_vote WHERE app_id = %s"
        adr = (app_id,)
        self.cursor.execute(sql, adr)
        count_in_favor = 0
        count_against = 0
        for (vote,) in self.cursor:
            if vote:
                count_in_favor+=1
            else:
                count_against+=1
        return {"in_favor":count_in_favor, "against":count_against}

    def has_voted(self,app_id,voter_id):
        sql = "SELECT null FROM app_vote WHERE app_id = %s AND voter_id = %s "
        adr = (app_id,voter_id,)
        self.cursor.execute(sql, adr)
        return len(self.cursor.fetchall()) == 1

    def vote_for(self,app_id,voter_id,is_in_favor):
        sql = ""
        adr = None
        has_voted = self.has_voted(app_id,voter_id)
        if not has_voted:
            sql = "INSERT INTO app_vote (app_id,voter_id,is_in_favor) VALUES (%s, %s, %s)"
            adr = (app_id,voter_id,is_in_favor,)
        else:
            sql = "UPDATE app_vote SET is_in_favor=%s WHERE app_id = %s AND voter_id = %s"
            adr = (is_in_favor,app_id,voter_id,)
        self.cursor.execute(sql, adr)
        self.db.commit()
        return has_voted
if __name__ == "__main__":
    print("This File is not supposed to be the main file")
    exit()
