import discord as dc
import logging
import json
from decouple import config
import db_handler as dbh
import os

# Activating the venv
os.system("source ~/venvs/girbot/bin/activate")

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='GIRBotLog.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Setting Variables
token = config("token")
client = dc.Client(intents=dc.Intents.all())



client.run(token)