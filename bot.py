import discord
import logging
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
    if message.author == client.user:
        return
    
    if message.content.startswith('$test'):
        channel = message.channel
        await channel.send('Der Test hat geklappt!')
        print('Der Command "Test" wurde ausgeführt!')
        print('------------------------------------')
#Activity setzen
    if message.content.startswith('$activity'):
        activity = discord.Activity(name='over Discord', type=discord.ActivityType.watching)
        await client.change_presence(activity=activity)
        print('Der Bot-Status wurde gesetzt!')
        print('-----------------------------')
#Hier beginnt das Aufgaben erstellen; der Builder (Builder) und die Aufgabe (Aufgabe) wird herraus gefiltert, gespeichert und als Nachricht ausgegeben
    if message.content.startswith('$task add') and message.author in (guild.get_role('692409029384994938').members + guild.get_role('709719558189088809').members):
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
    if message.content.startswith('$task delete') and message.author in (guild.get_role('692409029384994938').members + guild.get_role('709719558189088809').members):
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
#Die Language Funktion
#Sprachen hinzufügen
    if message.content.startswith('$language add'):
        channel = message.channel
        Sprache = message.content
        Sprache = Sprache.split()[2]
        Member = message.author.id
        if not str(Member) in data['Members']:
            data['Members'][str(Member)] = {}
        if not 'language' in data['Members'][str(Member)]:
            data['Members'][str(Member)]['language'] = []
        if not Sprache in data['Members'][str(Member)]['language']:
            data['Members'][str(Member)]['language'].append(Sprache)
            with open('GIRBot.json', 'w', encoding='utf8') as outfile:
                json.dump(data, outfile)
            await channel.send("The Language " + Sprache + " has been added")
        else:
            await channel.send("The Language has already been added!")
#Sprachen auslesen
    if message.content.startswith('$languages'):
        channel = message.channel
        Inhalt = message.content
        Inhalt = Inhalt.split()[1:]
        reqMember = Inhalt[0].replace('@', '')
        reqMember = str(guild.get_member_named(reqMember).id)
        if not reqMember in data['Members'] or not 'language' in (data['Members'][reqMember]) or len(data['Members'][reqMember]['language']) == 0:
            await channel.send("The Member " + guild.get_member(int(reqMember)).name + " didn't set a Language!")
        else:
            i = 0
            await channel.send("The Languages of " + Inhalt[0].replace('@', '') + " are:")
            for lang in data['Members'][reqMember]['language']:
                i+=1
                await channel.send(str(i) + ". " + lang)
#Sprache löschen
    if message.content.startswith('$language remove'):
        channel = message.channel
        Inhalt = message.content
        lang = Inhalt.split()[2]
        Member = str(message.author.id)
        if Member in data['Members']:
            if 'language' in data['Members'][Member] and lang in (data['Members'][Member]['language']):
                data['Members'][Member]['language'].remove(lang)
                with open('GIRBot.json', 'w', encoding='utf8') as outfile:
                    json.dump(data, outfile)
                await channel.send("The Language has been deleted!")
            else:
                await channel.send("The Language your trying to delete doesn't exist...")
        else:
            print(Member, "in Members not found!")
            await channel.send("It seems like you didn't add a Language yet! Try adding one first")


    
client.run(token)