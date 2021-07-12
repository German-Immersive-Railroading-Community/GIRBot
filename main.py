import logging
from os import name
from sys import prefix

import discord as dc
import discord_slash as dcs
from decouple import config
from discord.ext import commands as cmd
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import (create_choice, create_option,
                                                 create_permission)

from db_handler import Db_interface as Dbi
from variables import *

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
client = cmd.Bot(command_prefix=bot_prefix, intents=dc.Intents.all())
slash = dcs.SlashCommand(client, sync_commands=True)
db = Dbi()

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
    await ctx.send(content=f"Dem Nutzer {person.display_name} wurde die Developer-Rolle gegeben!", hidden=True)


# Commands with DB use

@slash.slash(
    name="Apply",
    description="Apply for a Role on the server.",
    guild_ids=guild_id,
    options=[
        create_option(
            name="role",
            description="The role you want to apply for.",
            option_type=8,
            required=True
        ),
        create_option(
            name="text",
            description="A nice little text why you want the role.",
            option_type=3,
            required=False
        )
    ]
)
async def application(ctx, role, text="No text has been given!"):
    # TODO Check in Class 'Db_interface' function is_member = True, else cancel with message | HOLDED! Need the register-plugin-side first
    # if not db.is_member(ctx.author.id) == True:
    #    await ctx.send(content="You are not registered! Please register first using our register function!")

    if db.count_app(ctx.author.id) > 2:
        await ctx.send(content="You already have 2 Applications open! Please wait for them to be processed.", hidden=True)
    elif db.count_app(ctx.author.id, role=role.id) > 0:
        await ctx.send(content="You already have a pending application for this role! Please wait for it to be processed.", hidden=True)
    else:
        app_embed = dc.Embed(
            title=role.name,
            description=text,
            color=role.colour.value
        ).set_author(name=ctx.author.display_name)
        app_id = db.new_id()
        app_embed.set_footer(text=str(app_id))
        channel = client.get_channel(sent_app_channel_id)
        embed_message = await channel.send(embed=app_embed)
        db.add_app(ctx.author.id, role.id, embed_message.id, app_id=app_id)
        await ctx.send(content="Thank you for applying! You will be notified when we processed it.", hidden=True)


@slash.slash(
    name="Vote",
    description="Vote for a application",
    guild_ids=guild_id,
    default_permission=False,
    permissions={
        girc_guild_id: [
            create_permission(admin_role_id,
                              SlashCommandPermissionType.ROLE, True
                              ),
            create_permission(owner_role_id,
                              SlashCommandPermissionType.ROLE, True
                              )
        ]
    },
    options=[
        create_option(
            name="id",
            description="The ID of the application (see footer).",
            option_type=4,
            required=True
        ),
        create_option(
            name="vote",
            description="Wether or not the application is okay with you.",
            option_type=5,
            required=True
        )
    ]
)
async def vote(ctx, id, vote):
    if not ctx.channel.id == sent_app_channel_id:
        await ctx.send(content="This is the wrong channel!", hidden=True)
        return
    if db.check_id_free(id):
        await ctx.send(content="This App ID does not exist!", hidden=True)
        return
    db.vote_for(id, ctx.author.id, vote)
    await ctx.send(content="You succesfully voted.")
    votes = db.check_vote(id)
    voters = len([voter for voter in client.get_channel(sent_app_channel_id).members
                  if ctx.guild.get_role(role_id=admin_role_id) in voter.roles
                  or ctx.guild.get_role(owner_role_id) in voter.roles])
    app_data = db.get_app(id)
    if votes["in_favor"] > voters//2:
        role_to_give = ctx.guild.get_role(role_id=app_data["role"])
        await ctx.guild.get_member(app_data["member_id"]).add_roles(role_to_give)
        app_message = await ctx.channel.fetch_message(app_data["message_id"])
        await app_message.add_reaction("\N{White Heavy Check Mark}")
        dms = await ctx.guild.get_member(app_data["member_id"]).create_dm()
        await dms.send(content=f"Hey you! Your application for the role {role_to_give.name} has been accepted! Have fun with your new role.")
        db.del_app(id)
    elif votes["against"] > voters//2:
        role_to_give = ctx.guild.get_role(role_id=app_data["role"])
        app_message = await ctx.channel.fetch_message(app_data["message_id"])
        await app_message.add_reaction("\N{No Entry Sign}")
        dms = await ctx.guild.get_member(app_data["member_id"]).create_dm()
        await dms.send(content=f"Hey you! Your application for the role {role_to_give.name} has been rejected! For further information, please contact an Administrator or Owner.")
        db.del_app(id)

client.run(token)
