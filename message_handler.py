import discord



def person(client,name):
    guild=client.guilds[0]
    if name[3:-1] in [str(i.id) for i in guild.members]:
        pers = guild.get_member(int(name[3:-1]))
    else:
        members=[i.name.lower() for i in guild.members]
        liste=[i for i,x in enumerate(members) if x == name.lower()]
        if len(liste)>0:
            pers= guild.members[liste[0]]
        else:
            return None
    return pers


class command:
    def __init__(self, message, client, guild, DebugMode):
        self.code = 404
        self.fct_code = None
        self.parameters=[]
        self.guild = guild
        self.DebugMode = DebugMode
        channel = message.channel
        self.parameters.append(channel)
#Einfacher test
        if message.content=="$test":
            self.code=200
            self.fct_code=0
#Ignore Bot messages and other things not starting with the prefix
        elif not message.content.startswith('$') or message.content.startswith('%'):
            pass
#Activity
        elif message.content.startswith('$activity'):
            self.code=200
            self.fct_code=1
#-----------------------------------------------------------------------------------------------------------------------
#Task Handling
#-----------------------------------------------------------------------------------------------------------------------
#Task add
        elif message.content.startswith('$task add') and message.author in (guild.get_role(692409029384994938).members):
            self.fct_code=10
            Inhalt = message.content.split()[2:]
            builder = Inhalt[0]
            task = " ".join(Inhalt[1:])
            builder = person(client,builder)
            if builder != None:
                self.code = 200
                self.parameters.append(builder)
                self.parameters.append(task)
            else:
                self.code = 300
#Task abfrage
        elif message.content.startswith('$tasks'):
            self.fct_code=11
            self.code=200
            self.parameters.append(message.author)
#Task löschen
        elif message.content.startswith('$task delete') and message.author in (guild.get_role(692409029384994938).members):
            self.fct_code=12
            Inhalt = message.content.split()[2:]
            if len(Inhalt)!=2:
                self.code= 301
                return
            builder = Inhalt[0]
            builder = person(client,builder)
            if builder == None:
                self.code= 300
                return
            try:
                taskID = int(Inhalt[1])-1
                self.code=200
                self.parameters.append(builder)
                self.parameters.append(taskID)
            except:
                self.code = 102
#-----------------------------------------------------------------------------------------------------------------------
#Sprachen
#-----------------------------------------------------------------------------------------------------------------------
#Sprache hinzufügen
        elif message.content.startswith('$language add') or message.content.startswith('language set'):
            self.fct_code=20
            if len(message.content)>2:
                lang = " ".join(message.content.split()[2:])
                self.code=200
                self.parameters.append(lang)
                self.parameters.append(message.author)
            else:
                self.code=301
#Sprache löschen
        elif message.content.startswith('$language remove') or message.content.startswith('$language delete'):
            self.fct_code=21
            if len(message.content.split())==3:
                lang = message.content.split()[2]
                self.code=200
                self.parameters.append(lang)
                self.parameters.append(message.author)

            else:
                self.code=400
#Sprachen Abfragen
        elif message.content.startswith("$languages"):
            self.fct_code=22
            if len(message.content)>1:
                Inhalt = message.content.split()[1:]
                reqMember = " ".join(Inhalt)
                reqMember = person(client,reqMember)
                if reqMember == None:
                    self.code = 300
                    return
                else:
                    self.code = 200
                    self.parameters.append(reqMember)
#-----------------------------------------------------------------------------------------------------------------------
#Debbuging
#-----------------------------------------------------------------------------------------------------------------------
#Relog the Bot
        elif (message.content.startswith("%Restart") or message.content.startswith("%Relog")) and message.author in (guild.get_role(709719558189088809).members):
            self.fct_code = 30
            self.code = 200
#Activating Debug
        elif message.content.startswith("%DebugMode true") and message.author in (guild.get_role(709719558189088809).members):
            self.fct_code = 31
            self.code = 200
#Deactivating Debug
        elif message.content.startswith("%DebugMode false") and message.author in (guild.get_role(709719558189088809).members):
            self.fct_code = 32
            self.code = 200
#Outputing a Message in the Console
        elif message.content.startswith("%message") and self.DebugMode == True and message.author in (guild.get_role(709719558189088809).members):
            self.fct_code = 33
            self.code = 200