import logging
import discord
import json

#Test Command
def command_test(para):
    await channel.send('Der Test hat geklappt!')
    print('Der Command "Test" wurde ausgeführt!')
    print('----------------------------------------------')

#Command for setting Activity
def command_activity(para):
    activity = discord.Activity(name='Discord', type=discord.ActivityType.watching)
    await client.change_presence(activity=activity)
    print('Der Bot-Status wurde gesetzt!')
    print('----------------------------------------------')

#Start of the Builder-Task-Tool
#Creating a Task
def command_create_BuilderTask(para):
    channel = para[0]
    builder = para[1]
    task = para[2]
    builder = builder.id
    if not builder.id in data['Builders']:
        data['Builders'][builder.id] = []
    data['Builders'][builder.id].append(Aufgabe)
    with open('GIRBot.json', 'w', encoding='utf8') as outfile:
        json.dump(data, outfile)
    await channel.send("Die neue Aufgabe von " + builder.name + " ist " + Aufgabe)

#Check your tasks
def command_check_BuilderTask(para):
    channel = para[0]
    builder = para[1]
    if not builder.id in data['Builders']:
        await channel.send("You aren't a registered Builder!")
    else:
        i = 0
        for p in data['Builders'][builder.id]:
            i+=1
            await channel.send(str(i) + ". " + p)

#Delete a Task
def command_delete_BuilderTask(para):
    channel = para[0]
    builder = para[1]
    taskID = para[2]
    if builder.id in data['Builders']:
        if taskID < len(data['Builders'][builder.id]):
            deletedTask = data['Builders'][builder.id][taskID]
            del data['Builders'][builder.id][taskID]
            with open('GIRBot.json', 'w', encoding='utf8') as outfile:
                json.dump(data, outfile)
            await channel.send("Die Aufgabe " + deletedTask + " wurde gelöscht")
        else:
            await channel.send('Aufgabe nicht gefunden!')
    else:
        print(builder.name, 'in Tasklist not found!')
        print('----------------------------------------------')
        await channel.send("Der Builder " + builder.name + "wurde nicht gefunden!")
#End of the Builder-Task-Tool

#Start of the Language-Tool
#Adding a Language
def command_add_language(para):
    channel = para[0]
    lang = para[1]
    member = para[2]
    if not member.id in data['Members']:
        data['Members'][member.id] = {}
    if not 'language' in data['Members'][member.id]:
        data['Members'][member.id]['language'] = []
    if not lang in data['Members'][member.id]['language']:
        data['Members'][member.id]['language'].append(Sprache)
        with open('GIRBot.json', 'w', encoding='utf8') as outfile:
            json.dump(data, outfile)
        await channel.send("The Language " + lang + " has been added")
    else:
        await channel.send("The Language has already been added!")