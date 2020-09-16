import discord
import logging
import json
import message_handler as mh
import functions as fcts

with open('token.txt') as file:
    token = file.readline()
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='GIRBotLog.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
client = discord.Client()
DebugMode = False
global data
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
    global data
    print(message.content)
    cmd  = mh.command(message,client)
    if cmd.code==200:
        if cmd.fct_code == 0:
            await fcts.command_test(cmd.parameters)
        elif cmd.fct_code == 1:
            await fcts.command_activity(cmd.parameters+[client])
        elif cmd.fct_code == 10:
            data = await fcts.command_create_BuilderTask(cmd.parameters+[data])
        elif cmd.fct_code == 11:
            data = await fcts.command_check_BuilderTask(cmd.parameters+[data])
        elif cmd.fct_code == 12:
            data = await fcts.command_delete_BuilderTask(cmd.parameters+[data])
        elif cmd.fct_code == 20:
            data = await fcts.command_add_language(cmd.parameters+[data])
        elif cmd.fct_code == 22:
            data = await fcts.command_check_language(cmd.parameters+[data])
        elif cmd.fct_code == 21:
            data = await fcts.command_delete_language(cmd.parameters+[data])
    else:
        print(cmd.code)
client.run(token) 