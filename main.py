import logging
import random as rd
from os import name
from sys import prefix

import interactions as dc
from decouple import config

from db_handler import Db_interface as Dbi
from variables import *

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(
    filename='GIRBotLog.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Setting Variables
client = dc.Client(token)
db = Dbi()

# Standard shit

@client.event
async def on_ready():
    print("Let them trains roll!")

# Initializing the Slash Commands
# Commands without DB use

@client.command(
    name="devset",
    description="Give someone the Dev-Role... Spooky",
    scope=girc_guild_id,
    default_permission=False,
    options=[
        dc.Option(
            name="person",
            description="The Person you wanna give power to.",
            type=dc.OptionType.USER,
            required=True
        ),
        dc.Option(
            name="language",
            description="The language of the person.",
            type=dc.OptionType.STRING,
            required=True,
            choices=[
                dc.Choice(
                    name="German",
                    value=name
                ),
                dc.Choice(
                    name="English",
                    value=name
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


@client.command(
    name="idea",
    description="Send us a wish or idea you have!",
    scope=girc_guild_id,
    options=[
        dc.Option(
            name="type",
            description="Is it an idea or wish?",
            type=dc.OptionType.STRING,
            required=True,
            choices=[
                dc.Choice(
                    name="Idea",
                    value=name
                ),
                dc.Choice(
                    name="Wish",
                    value=name
                )
            ]
        ),
        dc.Option(
            name="text",
            description="Your idea or wish you want to tell us",
            type=dc.OptionType.STRING,
            required=True
        )
    ]
)
async def ideas_wishes(ctx, type, text):
    idea_embed = dc.Embed(
        title=type,
        description=text,
        color=rd.randint(0, 0xFFFFFF),
        author=ctx.author.display_name
    )
    channel = client.get_channel(sent_idea_channel_id)
    embed_message = await channel.send(embed=idea_embed)
    await embed_message.add_reaction("\N{White Heavy Check Mark}")
    await embed_message.add_reaction("\N{No Entry Sign}")
    await ctx.send(content=f"Thank you! Your {type} has been sent to us.", hidden=True)


# Commands with DB use

@client.command(
    name="apply",
    description="Apply for a role on the server.",
    scope=girc_guild_id,
    options=[
        dc.Option(
            name="role",
            description="The role you want to apply for.",
            type=dc.OptionType.ROLE,
            required=True
        ),
        dc.Option(
            name="text",
            description="A nice little text why you want the role",
            type=dc.OptionType.STRING,
            required=True
        )
    ]
)
async def application(ctx, role, text):
    # TODO Check in Class 'Db_interface' function is_member = True, else cancel with message | HOLDED! Need the register-plugin-side first
    # if not db.is_member(ctx.author.id) == True:
    #    await ctx.send(content="You are not registered! Please register first using our register function!")
    if db.count_app(str(ctx.author.id)) > 2:
        await ctx.send(content="You already have 2 Applications open! Please wait for them to be processed.", hidden=True)
    elif db.count_app(str(ctx.author.id), role=str(role.id)) > 0:
        await ctx.send(content="You already have a pending application for this role! Please wait for it to be processed.", hidden=True)
    else:
        app_embed = dc.Embed(
            title=role.name,
            description=text,
            color=role.color,
            author=ctx.author.display_name
        )
        app_id = db.new_id()
        app_embed.set_footer(text=str(app_id))
        channel = client.get_channel(sent_app_channel_id)
        embed_message = await channel.send(embed=app_embed)
        db.add_app(ctx.author.id, role.id, embed_message.id, app_id=app_id)
        await ctx.send(content="Thank you for applying! You will be notified when we processed it.", hidden=True)


@client.command(
    name="vote",
    description="Vote for an application.",
    scope=girc_guild_id,
    default_permission=False,
    options=[
        dc.Option(
            name="id",
            description="The ID of the application (see footer).",
            type=dc.OptionType.INTEGER,
            required=True
        ),
        dc.Option(
            name="vote",
            description="Wether or not the application is okay with you.",
            type=dc.OptionType.BOOLEAN,
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
    await ctx.send(content=f"You succesfully voted for {id}.")
    votes = db.check_vote(id)
    voters = len([voter for voter in client.get_channel(sent_app_channel_id).members
                  if ctx.guild.get_role(role_id=admin_role_id) in voter.roles
                  or ctx.guild.get_role(owner_role_id) in voter.roles])
    app_data = db.get_app(id)
    app_message = await ctx.channel.fetch_message(app_data["message_id"])
    if votes["in_favor"] > voters//2:
        role_to_give = ctx.guild.get_role(role_id=app_data["role"])
        await ctx.guild.get_member(app_data["member_id"]).add_roles(role_to_give)
        await app_message.add_reaction("\N{White Heavy Check Mark}")
        dms = await ctx.guild.get_member(app_data["member_id"]).create_dm()
        await dms.send(content=f"Hey you! Your application for the role {role_to_give.name} has been accepted! Have fun with your new role.")
        db.del_app(id)
    elif votes["against"] > voters//2:
        role_to_give = ctx.guild.get_role(role_id=app_data["role"])
        await app_message.add_reaction("\N{No Entry Sign}")
        dms = await ctx.guild.get_member(app_data["member_id"]).create_dm()
        await dms.send(content=f"Hey you! Your application for the role {role_to_give.name} has been rejected! For further information, please contact an Administrator or Owner.")
        db.del_app(id)

client.start()
