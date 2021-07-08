from sys import prefix
import discord as dc
import logging
from decouple import config
#import db_handler as dbh
from discord.ext import commands as cmd
# DC Slash
import discord_slash as dcs
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='GIRBotLog.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Setting Variables
bot_prefix = "ANiceAndLongPrefixSoNoOneUsesIt"
token = config("token")
client = cmd.Bot(command_prefix=bot_prefix, intents=dc.Intents.all())
slash = dcs.SlashCommand(client, sync_commands=True)

guild_id = str(config("guild_id")).split(",")
guild_id = [int(i) for i in guild_id]
girc_guild_id = int(guild_id[0])

head_dev_role_id = int(config("head_dev_role_id"))
dev_role_id = int(config("dev_role_id"))
everyone_role = config("everyone_role_id")

# Standard shit


@client.event
async def on_ready():
    print("Let them trains roll!")

# Initializing the Slash Commands
# Commands without DB use


@slash.slash(
    name="DevSet",
    description="Give someone the Dev-Role... Spooky",
    guild_ids=guild_id,
    default_permission=False,
    permissions={
        girc_guild_id: [
                create_permission(head_dev_role_id,
                                  SlashCommandPermissionType.ROLE, True),
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
                create_choice(
                        name="German",
                        value="German"
                ),
                create_choice(
                    name="English",
                    value="English"
                )
            ]
        )
    ]
)
async def devset(ctx, person, language):
    await person.add_roles(ctx.guild.get_role(role_id=dev_role_id))
    await person.add_roles(dc.utils.get(ctx.guild.roles,
                                        name=language + " Member"))
    await ctx.send(content=f"Dem Nutzer {person.display_name} wurde die Developer-Rolle gegeben!")


client.run(token)
