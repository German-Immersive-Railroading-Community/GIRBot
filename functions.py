import logging
import discord
import json
import time
if __name__ == "__main__":
    global data
    data = {}

#Test Command
def command_test(para):
    channel = para[0]
    await channel.send('Der Test hat geklappt!')
    print('Der Command "Test" wurde ausgeführt!')
    print('----------------------------------------------')

#Command for setting Activity
def command_activity(para):
    client = para[0]
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
    data['Builders'][builder.id].append(task)
    with open('GIRBot.json', 'w', encoding='utf8') as outfile:
        json.dump(data, outfile)
    await channel.send("Die neue Aufgabe von " + builder.name + " ist " + task)

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
        data['Members'][member.id]['language'].append(lang)
        with open('GIRBot.json', 'w', encoding='utf8') as outfile:
            json.dump(data, outfile)
        await channel.send("The Language " + lang + " has been added")
    else:
        await channel.send("The Language has already been added!")

#Checking the Languages
def command_check_language(para):
    channel = para[0]
    reqMember = para[1]
    if not reqMember.id in data['Members'] or not 'language' in (data['Members'][reqMember.id]) or len(data['Members'][reqMember.id]['language']) == 0:
        await channel.send("The Member " + reqMember.name + " didn't set a Language!")
    else:
        i = 0
        await channel.send("The Languages of " + reqMember.name + " are:")
        for lang in data['Members'][reqMember.id]['language']:
            i+=1
            await channel.send(str(i) + ". " + lang)

#Deleting a Language
def command_delete_language(para):
    channel = para[0]
    member = para[1]
    lang = para[2]
    if member.id in data['Members']:
        if 'language' in data['Members'][member.id] and lang in (data['Members'][member.id]['language']):
            data['Members'][member.id]['language'].remove(lang)
            with open('GIRBot.json', 'w', encoding='utf8') as outfile:
                json.dump(data, outfile)
            await channel.send("The Language has been deleted!")
        else:
            await channel.send("The Language your trying to delete doesn't exist...")
    else:
        await channel.send("It seems like you didn't add a Language yet! Try adding one first")
#End of the Language-Tool

#Restart the Bot
def command_restart(para):
    token = para[0]
    client = para[1]
    await client.close()
    time.sleep(3)
    await client.login(token, bot=True)

#Start of the Debugging Commands
#Activating Debug
def debugging_command_DebugTrue(para):
    developer = para[0]
    #Setting the "DebugMode" Variable to true
    print('Der Nutzer', developer.name, 'hat den Debug Mode aktiviert!')
    print('----------------------------------------------')

#Deactivating Debug
def debugging_command_DebugFalse(para):
    developer = para[0]
    #Setting the "DebugMode" Variable to false
    print('Der Nutzer', developer.name, 'hat den Debug Mode deaktiviert!')
    print('----------------------------------------------')

#Outputing a Message in the Console
def debugging_command_message(para):
    channel = para[0]
    message = para[1]
    developer = para[2]
    print('Der Nutzer', developer.name, 'hat die Nachricht', message, 'im Channel', channel, 'um %(asctime)s geschrieben!')
    print('----------------------------------------------')
    await channel.send(channel + ", " + developer.name + ", " + message)