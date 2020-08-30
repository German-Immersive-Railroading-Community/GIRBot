import discord
import logging
from discord.ext import commands
import json

with open('token.txt') as file:
    token = file.readline()
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='GIRBot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
client = discord.Client()
data = {}
data['Builders'] = {}
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
    if message.author == client.user:
        return
    
    if message.content.startswith('$test'):
        channel = message.channel
        await channel.send('Der Test hat geklappt!')
        print('Der Command "Test" wurde ausgeführt!')
        print('------------------------------------')
    
    if message.content.startswith('$activity'):
        activity = discord.Activity(name='over Discord', type=discord.ActivityType.watching)
        await client.change_presence(activity=activity)
        print('Der Bot-Status wurde gesetzt!')
        print('-----------------------------')
    
    if message.content.startswith('$abc'):
        channel = message.channel
        await channel.send('Du kannst den Anfang des ABCs!')
#Hier beginnt das Aufgaben erstellen; der Builder (Builder) und die Aufgabe (Aufgabe) wird herraus gefiltert, gespeichert und als Nachricht ausgegeben
    if message.content.startswith('$task add'):
        channel = message.channel
        Inhalt = message.content
        Inhalt = Inhalt.split()[2:]
        Builder = Inhalt[0]
        Aufgabe = " ".join(Inhalt[1:])
        Builder = guild.get_member_named(Builder).id
        if not str(Builder) in data['Builders']:
            data['Builders'][str(Builder)] = []
        data['Builders'][str(Builder)].append(Aufgabe)
        with open('GIRBot.json', 'w', encoding='utf8') as outfile:
            json.dump(data, outfile)
        await channel.send("Die neue Aufgabe von" + " " + guild.get_member(Builder).name + " " + "ist" + " " + Aufgabe)
#Auslesen der Aufgaben
    if message.content.startswith('$tasks'):
        channel = message.channel
        Builder = message.author.id
        i = 0
        for p in data['Builders'][str(Builder)]:
            i+=1
            await channel.send(str(i) + ". " + p)
#Löschen der Aufgaben
    if message.content.startswith('$task delete'):
        channel = message.channel
        Inhalt = message.content
        Inhalt = Inhalt.split()[2:]
        Builder = Inhalt[0]
        taskID = int(Inhalt[1])-1
        Builder = str(guild.get_member_named(Builder).id)
        if Builder in data['Builders']:
            if taskID < len(data['Builders'][Builder]):
                deletedTask = data['Builders'][Builder][taskID]
                del data['Builders'][Builder][taskID]
                with open('GIRBot.json', 'w', encoding='utf8') as outfile:
                    json.dump(data, outfile)
                await channel.send("Die Aufgabe " + deletedTask + " wurde gelöscht")
            else:
                await channel.send('Aufgabe nicht gefunden!')
        else:
            print(Builder, "in Tasklist not found!")
            await channel.send("Der Builder " + guild.get_member(Builder).name + "wurde nicht gefunden!")
        


    
client.run(token)