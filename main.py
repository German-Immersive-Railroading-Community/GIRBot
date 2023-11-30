import configparser as cp
import sqlite3 as sql
from os.path import exists

import interactions as i

config = cp.ConfigParser()
config.read("config.ini")
bot = i.Client(token=config["General"]["token"], disable_dm_commands=True)
if config["General"]["sentry_token"] != "":
    bot.load_extension("interactions.ext.sentry",
                       token=config["General"]["sentry_token"])
bot.load_extension("interactions.ext.jurigged")


def setup_save():
    if not exists("data.json"):
        with open("data.json", "w") as f:
            f.write("{}")
    con = sql.connect("data.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS roles (
        role_id INTEGER PRIMARY KEY,
        name TEXT,
        short_description TEXT,
        long_description TEXT,
        enabled BOOLEAN
    )""")


setup_save()


@i.listen()
async def on_startup():
    print("Bot started.")

bot.load_extension("extensions.application")
bot.load_extension("extensions.mod")

bot.start()
