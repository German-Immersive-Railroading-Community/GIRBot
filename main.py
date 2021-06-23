from sys import prefix
import discord as dc
import logging
import json
from decouple import config
#import db_handler as dbh
import os
from discord.ext import commands as cmd
# DC Slash
import discord_slash as dcs
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='GIRBotLog.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Setting Variables
bot_prefix = "ANiceAndLongPrefixSoNoOneUsesIt"
token = config("token")
client = cmd.Bot(command_prefix=bot_prefix, intents=dc.Intents.all())
slash = dcs.SlashCommand(client, sync_commands=True)
guild_id = str(config("guild_id")).split(",")
girc_guild_id = int(guild_id[0])
girc_guild = client.get_guild(int(690967067855421470))
print(girc_guild)
head_dev_role_id = int(config("head_dev_role_id"))
everyone_role = girc_guild.default_role
dev_role_id = int(config("dev_role_id"))


# Standard shit
@client.event
async def on_ready():
    print("Let them trains roll!")

# Initializing the Slash Commands 
# Commands without DB use
@slash.slash(
        name="Set someone Developer",
        description="Give someone the Dev-Role... Spooky",
        guild_ids=guild_id,
        permissions={
            girc_guild: [
                create_permission(head_dev_role_id, SlashCommandPermissionType.ROLE, True),
                create_permission(everyone_role.id, SlashCommandPermissionType.ROLE, False)
            ]
        },
        options=[
            create_option(
                name="person",
                description="The Person you wanna give power to.",
                option_type=6,
                required=True
                ),
            create_option(
                name="language",
                description="The language of the person.",
                option_type=3,
                required=True,
                choices=[
                    create_option(
                        name="German",
                        value="German"
                        ),
                    create_option(
                        name="English",
                        value="English"
                        )
                    ]
                )
            ]
        )
async def hug(ctx, person, language):
    person.add_roles(girc_guild.get_role(dev_role_id))
    person.add_roles(dc.utils.get(girc_guild.roles, name = language + " Member").id)
    await ctx.send(content=f"Dem Nutzer {person.display_name} wurde die Developer-Rolle gegeben!")


client.run(token)