import discord



def person(client,name):
    guild=client.guilds[0]
    if name in guild.members:
        pers = guild.get_member_named(name).id
        guild = client.guilds[0]
    elif name[3:-1] in [str(i.id) for i in guild.members]:
        pers = guild.get_member(int(name[3:-1]))
    else:
        members=[i.name.lower() for i in guild.members]
        liste=[i for i,x in enumerate(members) if x == name]
        if len(liste)>0:
            pers= guild.members[liste[0]]
        else:
            return None
    return pers


class command:
    code = 404
    fct_code = None
    parameters=[]
    def __init__(self, message, client):
        channel = message.channel
        self.parameters.append(channel)
#Einfacher test
        if message.content=="$test":
            self.code=200
            self.fct_code=0
#Activity
        elif message.content.startswith('$activity'):
            self.code=200
            self.fct_code=1
#-----------------------------------------------------------------------------------------------------------------------
#Task Handling
#-----------------------------------------------------------------------------------------------------------------------
#Task add
        elif message.content.startswith('$task add'):
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
        elif message.content.startswith('$task delete'):
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
        elif message.content.startswith('$language add'):
            self.fct_code=20
            if len(message.content)>2:
                lang = " ".join(lang.split()[2:])
                self.code=200
                self.parameters.append(lang)
            else:
                self.code=301
#Sprache löschen
        elif message.content.startswith('$language remove'):
            self.fct_code=21
            if len(message.content)==3:
                try:
                    nmbr = int(message.content.split()[3])
                    self.code=200
                    self.parameters.append(nmbr)
                except:
                    self.code = 102

            else:
                self.code=400
#Sprachen Abfragen
        elif message.content.startswith("$languages"):
            self.fct_code=22
            if len(message.content)>1:
                Inhalt = Inhalt.split()[1:]
                reqMember = " ".join(Inhalt)
                reqMember = person(client,reqMember)
                if reqMember == None:
                    self.code = 300
                    return
                else:
                    self.code = 200
                    self.parameters.append(reqMember)
