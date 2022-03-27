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
    raw_girc_guild = await client._http.get_guild(girc_guild_id)
    girc_guild = dc.Guild(**raw_girc_guild, _client=client._http)
    await girc_guild.add_member_role(dev_role_id, int(person.id))
    await girc_guild.add_member_role(get_role_from_name(language + " Member").id, int(person.id))
    await ctx.send(content=f"Dem Nutzer {person.display_name} wurde die Developer-Rolle gegeben!", ephemeral=True)


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
                    value="Idea"
                ),
                dc.Choice(
                    name="Wish",
                    value="Wish"
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
        title=str(type),
        description=text,
        color=rd.randint(0, 0xFFFFFF),
        author=dc.EmbedAuthor(name=str(ctx.author.nick))
    )
    raw_channel = await client._http.get_channel(sent_idea_channel_id)
    channel = dc.Channel(**raw_channel, _client=client._http)
    embed_message = await channel.send(embeds=idea_embed)
    await client._http.create_reaction(int(channel.id), int(embed_message.id), "\N{White Heavy Check Mark}")
    await client._http.create_reaction(int(channel.id), int(embed_message.id), "\N{No Entry Sign}")
    await ctx.send(content=f"Thank you! Your {type} has been sent to us.", ephemeral=True)


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
        await ctx.send(content="You already have 2 Applications open! Please wait for them to be processed.", ephemeral=True)
    elif db.count_app(str(ctx.author.id), role=str(role.id)) > 0:
        await ctx.send(content="You already have a pending application for this role! Please wait for it to be processed.", ephemeral=True)
    else:
        app_id = db.new_id()
        app_embed = dc.Embed(
            title=role.name,
            description=text,
            color=role.color,
            author=dc.EmbedAuthor(name=ctx.author.nick),
            footer=dc.EmbedFooter(text=str(app_id))
        )
        # If this works I'm gonna cry
        raw_channel = await client._http.get_channel(sent_app_channel_id)
        channel = dc.Channel(**raw_channel, _client=client._http)
        embed_message = await channel.send(embeds=app_embed)
        db.add_app(str(ctx.author.id), str(role.id),
                   str(embed_message.id), app_id=app_id)
        await ctx.send(content="Thank you for applying! You will be notified when we processed it.", ephemeral=True)


@client.command(
    name="vote",
    description="Vote for an application.",
    scope=girc_guild_id,
    default_permission=True,
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
            type=dc.OptionType.STRING,
            required=True,
            choices=[
                dc.Choice(
                    name="Approve",
                    value="True"
                ),
                dc.Choice(
                    name="Decline",
                    value="False"
                )
            ]
        )
    ]
)
async def vote(ctx, id, vote):
    # Disclaimer: I know this could be way better... But: https://imgur.com/a/KTRc3vS
    # Setting some variables
    vote = True if vote == "True" else False
    raw_channel = await client._http.get_channel(sent_app_channel_id)
    sent_app_channel = dc.Channel(**raw_channel, _client=client._http)
    raw_girc_guild = await client._http.get_guild(girc_guild_id)
    girc_guild = dc.Guild(**raw_girc_guild, _client=client._http)

    # Checking if the channel and command usage is correct and the user
    # is allowed to vote on that specific role
    if not int(ctx.channel_id) == int(sent_app_channel_id):
        await ctx.send(content="This is the wrong channel!", ephemeral=True)
        return
    if db.check_id_free(id):
        await ctx.send(content="This App ID does not exist!", ephemeral=True)
        return
    app_data = db.get_app(id)
    app_role_id = app_data["role"]
    if int(app_role_id) in head_voters.keys():
        app_role = await girc_guild.get_role(head_voters[app_role_id][0])
        if app_role_id == pr_role_id and ctx.author.id != head_pr_user_id:
            await ctx.send(content="You are not allowed to vote for that role!")
            return
        role_names = []
        for r in ctx.author.roles:
            r = await girc_guild.get_role(r)
            role_names.append(r.name)
        if not app_role.name in role_names:
            await ctx.send(content="You are not allowed to vote for that role!")
            return

    # More setting/getting some stuff to process further
    db.vote_for(id, str(ctx.author.id), vote)
    await ctx.send(content=f"You succesfully voted for {id}.")
    votes = db.check_vote(id)
    app_message = await sent_app_channel.get_message(app_data["message_id"])
    role_to_give = await girc_guild.get_role(role_id=app_role_id)

    # Some functions so the part above looks better
    async def decline_app():
        await app_message.add_reaction("\N{No Entry Sign}")
        await client._http.create_reaction(int(sent_app_channel.id), int(app_data["message_id"]), "\N{No Entry Sign}")
        member = await girc_guild.get_member(app_data["member_id"])
        member.send(content =f"Hey you! Your application for the role {role_to_give.name} has been rejected! For further information, please contact an Administrator or Owner.")
        db.del_app(id)

    async def accept_app():
        await girc_guild.add_member_role(role_to_give, app_data["member_id"])
        await client._http.create_reaction(int(sent_app_channel.id), int(app_data["message_id"]), "\N{White Heavy Check Mark}")
        member = await girc_guild.get_member(app_data["member_id"])
        member.send(content = f"Hey you! Your application for the role {role_to_give.name} has been accepted! Have fun with your new role.")
        db.del_app(id)

    # giving the user the role and user feedback
    if not int(app_role_id) in head_voters.keys():
        await accept_app() if vote else decline_app()
    elif votes["in_favor"] >= head_voters[app_role_id][1]//2:
        await accept_app()
    elif votes["against"] >= head_voters[app_role_id][1]//2:
        await decline_app()


@client.command(
    name="test",
    description="Command to test stuff",
    scope=girc_guild_id,
)
async def test(ctx):
    raw_girc_guild = await client._http.get_guild(girc_guild_id)
    girc_guild = dc.Guild(**raw_girc_guild, _client=client._http)
    role = await girc_guild.get_role(head_voters[709719558189088809][0])
    print(role.name)
    await ctx.send(content="Nothing to see here!", ephemeral=True)


# Some self-written stuff

async def get_role_from_name(role_name, guild_id=girc_guild_id):
    """This is a helper function to get a Role Object based on the name of the role"""
    roles = await client._http.get_all_roles(guild_id)
    i = 0
    for role in roles:
        if role["name"] == role_name:
            raw_girc_guild = await client._http.get_guild(girc_guild_id)
            guild_object = dc.Guild(**raw_girc_guild, _client=client._http)
            return await guild_object.get_role(int(role["id"]))

client.start()
