import logging
import discord
import json
import time
import datetime as dt
if __name__ == "__main__":
    global data
    data = {}

#Test Command
async def command_test(para):
    channel = para[0]
    await channel.send('Der Test hat geklappt!')
    print('Der Command "Test" wurde ausgeführt!')
    print('----------------------------------------------')

#Command for setting Activity
async def command_activity(para):
    client = para[1]
    activity = discord.Activity(name='Discord', type=discord.ActivityType.watching)
    await client.change_presence(activity=activity)
    print('Der Bot-Status wurde gesetzt!')
    print('----------------------------------------------')

#Start of the Builder-Task-Tool
#Creating a Task
async def command_create_BuilderTask(para):
    channel = para[0]
    builder = para[1]
    task = para[2]
    data = para[3]
    if not builder.id in data['Builders']:
        data['Builders'][builder.id] = []
    data['Builders'][builder.id].append(task)
    with open('GIRBot.json', 'w', encoding='utf8') as outfile:
        json.dump(data, outfile)
    await channel.send("Die neue Aufgabe von " + builder.name + " ist " + task)
    return data

#Check your tasks
async def command_check_BuilderTask(para):
    channel = para[0]
    builder = para[1]
    data = para[2]
    if not str(builder.id) in data['Builders']:
        await channel.send("You aren't a registered Builder!")
    else:
        i = 0
        for p in data['Builders'][str(builder.id)]:
            i+=1
            await channel.send(str(i) + ". " + p)
    return data

#Delete a Task
async def command_delete_BuilderTask(para):
    channel = para[0]
    builder = para[1]
    taskID = para[2]
    data = para[3]
    if str(builder.id) in data['Builders']:
        if taskID < len(data['Builders'][str(builder.id)]):
            deletedTask = data['Builders'][str(builder.id)][taskID]
            del data['Builders'][str(builder.id)][taskID]
            with open('GIRBot.json', 'w', encoding='utf8') as outfile:
                json.dump(data, outfile)
            await channel.send("Die Aufgabe " + deletedTask + " wurde gelöscht")
        else:
            await channel.send('Aufgabe nicht gefunden!')
    else:
        print(builder.name, 'in Tasklist not found!')
        print('----------------------------------------------')
        await channel.send("Der Builder " + builder.name + " wurde nicht gefunden!")
    return data
#End of the Builder-Task-Tool

#Start of the Language-Tool
#Adding a Language
async def command_add_language(para):
    channel = para[0]
    lang = para[1]
    member = para[2]
    data = para[3]
    if not str(member.id) in data['Members']:
        data['Members'][str(member.id)] = {}
    if not 'language' in data['Members'][str(member.id)]:
        data['Members'][str(member.id)]['language'] = []
    if not lang in data['Members'][str(member.id)]['language']:
        data['Members'][str(member.id)]['language'].append(lang)
        with open('GIRBot.json', 'w', encoding='utf8') as outfile:
            json.dump(data, outfile)
        await channel.send("The Language " + lang + " has been added")
    else:
        await channel.send("The Language has already been added!")
    return data

#Checking the Languages
async def command_check_language(para):
    channel = para[0]
    reqMember = para[1]
    data = para[2]
    if not str(reqMember.id) in data['Members'] or not 'language' in (data['Members'][str(reqMember.id)]) or len(data['Members'][str(reqMember.id)]['language']) == 0:
        await channel.send("The Member " + reqMember.name + " didn't set a Language!")
    else:
        i = 0
        await channel.send("The Languages of " + reqMember.name + " are:")
        for lang in data['Members'][str(reqMember.id)]['language']:
            i+=1
            await channel.send(str(i) + ". " + lang)
    return data

#Deleting a Language
async def command_delete_language(para):
    channel = para[0]
    member = para[2]
    lang = para[1]
    data = para[3]
    if str(member.id) in data['Members']:
        if 'language' in data['Members'][str(member.id)] and lang in (data['Members'][str(member.id)]['language']):
            data['Members'][str(member.id)]['language'].remove(lang)
            with open('GIRBot.json', 'w', encoding='utf8') as outfile:
                json.dump(data, outfile)
            await channel.send("The Language has been deleted!")
        else:
            await channel.send("The Language your trying to delete doesn't exist...")
    else:
        await channel.send("It seems like you didn't add a Language yet! Try adding one first")
    return data
#End of the Language-Tool

#Restart the Bot
#Note: No, the Bot doesn't fuck itself up after that Command, IT'S A FEATURE! <3
#And nooo, I don't know why
async def command_restart(para):
    client = para[2]
    await client.logout()
    exit()

#Start of the Debugging Commands
#Activating Debug
async def debugging_command_DebugTrue(para):
    developer = para[1]
    data = para[2]
    data['GIRBot']['DebugMode'] = 'True'
    with open('GIRBot.json', 'w', encoding='utf8') as outfile:
        json.dump(data, outfile)
    print('Der Nutzer', developer.name, 'hat den Debug Mode aktiviert!')
    print('----------------------------------------------')

#Deactivating Debug
async def debugging_command_DebugFalse(para):
    developer = para[1]
    data = para[2]
    data['GIRBot']['DebugMode'] = 'False'
    with open('GIRBot.json', 'w', encoding='utf8') as outfile:
        json.dump(data, outfile)
    print('Der Nutzer', developer.name, 'hat den Debug Mode deaktiviert!')
    print('----------------------------------------------')

#Outputing a Message in the Console
async def debugging_command_message(para):
    channel = para[0]
    developer = para[1]
    message = para[2]
    print('Der Nutzer "', developer.name, '" hat die Nachricht "', message.content, '" im Channel "', channel.name, '" um ', dt.datetime.now().strftime("%H:%M:%S"), ' geschrieben!')
    print('----------------------------------------------')
    await channel.send(channel.name + ", " + developer.name + ", " + message.content)
#End of the Debbugging Commands

#Start of the Licensing-Tool
#Adding a License
async def licensing_adding_license(para):
    creator = para[1]
    data = para[2]
    license_number = para[3]
    driver = para[4]
    if license_number in data['GIRBot']['Licenses']:
        data['GIRBot']['Licenses'][license_number] = {}