import discord
import logging
import json
import message_handler as mh

with open('token.txt') as file:
    token = file.readline()
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='GIRBotLog.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
client = discord.Client()
DebugMode = False
data = {}
data['Builders'] = {}
data['Members'] = {}
try: 
    with open('GIRBot.json') as json_file:
        data = json.load(json_file)
except:
    print('JSON File (GIRBot.json) corrupted!')
    print('------------------------------------')

@client.event
async def on_ready():
    print('Wir sind jetzt als {0.user} online und bereit!'.format(client))
    print('----------------------------------------------')
    global guild
    guild = client.guilds[0]

@client.event
async def on_message(message):
    channel = message.channel
    print(message.content)
    cmd  = mh.command(message,client)

client.run(token) 