import random as rd

import mysql.connector as sql
from decouple import config
from mysql.connector.errors import OperationalError

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

    def reconnect(self) -> None:
        self.db.disconnect()
        self.db = sql.connect(
            host=str(config("host")),
            user=str(config("db_user")),
            password=str(config("db_password")),
            database=str(config("db_name"))
        )
        self.cursor = self.db.cursor()

    def stat_execute(self, func, sql: str, adr: tuple = ()) -> None:
        self.reconnect()
        ok = False
        while not ok:
            try:
                func(sql, adr)
                ok = True
            except OperationalError:
                self.reconnect()
                continue

    def status(self):
        self.stat_execute(self.cursor.execute, "SHOW TABLES")
        return self.cursor.fetchall()

    def add_app(self, user_id, role_id, message_id, app_id=0):
        if not app_id:
            app_id = self.new_id()
        elif not self.check_id_free(app_id):
            raise Exception("App ID already exists!")
        self.stat_execute(self.cursor.execute, "INSERT INTO Application (id,member_id,role,message_id) VALUES (%s, %s, %s, %s)",
                          (app_id, user_id, role_id, message_id,))
        self.db.commit()
        return app_id

    def is_member(self, id):
        self.stat_execute(self.cursor.execute,
                          "SELECT null FROM Member WHERE id = %s", (id,))
        return len(self.cursor.fetchall()) == 1

    def count_app(self, id, role=None):
        self.sql = ""
        self.adr = ""
        if role == None:
            self.sql = "SELECT null FROM Application WHERE member_id = %s"
            self.adr = (id,)
        else:
            self.sql = "SELECT null FROM Application WHERE member_id = %s AND role = %s"
            self.adr = (id, role,)
        self.stat_execute(self.cursor.execute, self.sql, self.adr)
        return len(self.cursor.fetchall())

    def new_id(self):
        for i in range(100):
            # Create new id with checksum%8==0
            app_id = rd.randint(100, 999)
            qs = sum(int(digit) for digit in str(app_id))
            checkd = 8-qs % 8
            app_id = app_id*10+checkd
            if self.check_id_free(app_id):
                return app_id
        raise Exception("No free application Id found")

    def check_id_free(self, app_id):
        # check if id already exist
        self.stat_execute(
            self.cursor.execute, "SELECT null FROM Application WHERE id = %s", (app_id,))
        return len(self.cursor.fetchall()) == 0

    def check_vote(self, app_id):
        self.stat_execute(
            self.cursor.execute, "SELECT is_in_favor FROM app_vote WHERE app_id = %s", (app_id,))
        count_in_favor = 0
        count_against = 0
        for (vote,) in self.cursor:
            if vote:
                count_in_favor += 1
            else:
                count_against += 1
        return {"in_favor": count_in_favor, "against": count_against}

    def has_voted(self, app_id, voter_id):
        self.stat_execute(
            self.cursor.execute, "SELECT null FROM app_vote WHERE app_id = %s AND voter_id = %s ", (app_id, voter_id,))
        return len(self.cursor.fetchall()) == 1

    def vote_for(self, app_id, voter_id, is_in_favor):
        self.sql = ""
        self.adr = None
        has_voted = self.has_voted(app_id, voter_id)
        if not has_voted:
            self.sql = "INSERT INTO app_vote (app_id,voter_id,is_in_favor) VALUES (%s, %s, %s)"
            self.adr = (app_id, voter_id, is_in_favor,)
        else:
            self.sql = "UPDATE app_vote SET is_in_favor=%s WHERE app_id = %s AND voter_id = %s"
            self.adr = (is_in_favor, app_id, voter_id,)
        self.stat_execute(self.cursor.execute, self.sql, self.adr)
        self.db.commit()
        return has_voted

    def del_app(self, app_id):
        self.stat_execute(
            self.cursor.execute, "DELETE Application,app_vote FROM Application LEFT JOIN app_vote ON Application.id = app_vote.app_id WHERE id = %s", (app_id,))
        self.db.commit()

    def get_app(self, app_id):
        self.stat_execute(
            self.cursor.execute, "SELECT member_id, role, message_id FROM Application WHERE id = %s", (app_id,))
        for (member_id, role, message_id) in self.cursor:
            return {"member_id": member_id, "role": role, "message_id": message_id}


if __name__ == "__main__":
    db_t = Db_interface()
    db_t.del_app(0)
