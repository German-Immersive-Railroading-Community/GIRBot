import configparser as cp
import json
import sqlite3 as sql
from asyncio import TimeoutError

import interactions as i
from interactions.ext.paginators import Paginator

scope_ids = []


class ApplicationCommand(i.Extension):
    def __init__(self, bot):
        self.config = cp.ConfigParser()
        self.config.read("config.ini")
        global scope_ids
        scope_ids = self.config["General"]["scope_ids"].split(",")
        self.con = sql.connect("data.db")
        self.cur = self.con.cursor()

    async def update_menus(self, guild: i.models.discord.guild.Guild):
        try:
            with open("data.json", "r") as f:
                data = json.load(f)
                info_channel = await guild.fetch_channel(data["channel_id"])
            info_message = await info_channel.fetch_message(data["info_message_id"])
        except KeyError:
            return
        info_options = []
        self.cur.execute("SELECT role_id, name FROM roles")
        for role_id, name in self.cur.fetchall():
            info_options.append(i.StringSelectOption(
                label=name,
                value=str(role_id)
            ))
        role_info_select: i.StringSelectMenu = info_message.components[0].components[0]
        role_info_select.options = info_options
        role_info_select.max_values = len(info_options)

        application_message = await info_channel.fetch_message(data["application_message_id"])
        options = []
        self.cur.execute("SELECT role_id, name FROM roles WHERE enabled = 1")
        for role_id, name in self.cur.fetchall():
            options.append(i.StringSelectOption(
                label=name,
                value=str(role_id)
            ))
        application_select: i.StringSelectMenu = application_message.components[0].components[0]
        application_select.options = options
        application_select.max_values = len(options)
        await info_message.edit(components=[role_info_select])
        await application_message.edit(components=[application_select])

    async def _enable_roles(self, ctx: i.ComponentContext):
        for role in ctx.values:
            role = await ctx.guild.fetch_role(int(role))
            self.cur.execute(
                "SELECT role_id FROM roles WHERE role_id = ?", (int(role.id),))
            if self.cur.fetchone() is None:
                self.cur.execute("INSERT INTO roles VALUES (?, ?, ?, ?, ?)",
                                 (int(role.id), role.name, "", "", True))
                self.con.commit()
            else:
                self.cur.execute(
                    "UPDATE roles SET enabled = 1 WHERE role_id = ?", (int(role.id),))
                self.con.commit()
        await self.update_menus(ctx.guild)

    @i.slash_command(
        name="application",
        description="Basis Command für die Bewerbung",
        scopes=scope_ids
    )
    async def application(self, ctx: i.SlashContext):
        pass

    @application.subcommand(
        sub_cmd_name="setup",
        sub_cmd_description="Setup für die Bewerbung",
        options=[
            i.SlashCommandOption(
                name="channel",
                description="Der Channel, in dem die Bewerbungen gestartet werden sollen",
                type=i.OptionType.CHANNEL,
                required=True,
                channel_types=[i.ChannelType.GUILD_TEXT]
            )
        ]
    )
    async def application_setup(self, ctx: i.SlashContext, channel: i.models.discord.channel.GuildText):
        setup_info_embed = i.Embed(
            title="GIRC Rollen Informationen",
            description="""Bitte wähle unten im Auswahlmenü eine Rolle aus, um Informationen zu dieser Rolle zu erhalten.\n
            Wähle 'Kurzbeschreibung' aus, um eine Kurzbeschreibung aller Rollen zu erhalten.""",
            color=i.RoleColors.DARK_BLUE.value,
            thumbnail=i.EmbedAttachment(
                url="https://cdn.discordapp.com/attachments/923199431447289916/923200094264774676/LogoDiscord.png"),
        )
        options = [i.StringSelectOption(
            label="Kurzbeschreibung",
            value="Kurzbeschreibung")]
        self.cur.execute("SELECT role_id, name FROM roles")
        for role_id, name in self.cur.fetchall():
            options.append(i.StringSelectOption(
                label=name,
                value=str(role_id)
            ))
        role_info_select = i.StringSelectMenu(
            custom_id="role_info_selectmenu",
            placeholder="Wähle eine Rolle aus",
            min_values=1,
            max_values=len(options),
            *options
        )
        setup_application_embed = i.Embed(
            title="GIRC Bewerbung",
            description="""Bitte wähle unten im Auswahlmenü eine Rolle aus, für die du dich bewerben möchtest.\
             Wenn eine der Rollen nicht angezeigt wird, kann man sich momentan nicht für diese Rolle bewerben.""",
            color=i.RoleColors.DARK_BLUE.value,
            thumbnail=i.EmbedAttachment(
                url="https://cdn.discordapp.com/attachments/923199431447289916/923200094264774676/LogoDiscord.png"),
        )
        options = []
        self.cur.execute("SELECT role_id, name FROM roles WHERE enabled = 1")
        for role_id, name in self.cur.fetchall():
            options.append(i.StringSelectOption(
                label=name,
                value=str(role_id)
            ))
        if len(options) == 0:
            await ctx.send("Es sind momentan keine Rollen verfügbar. Bitte aktiviere erst mindestens eine.", ephemeral=True)
            return
        application_select = i.StringSelectMenu(
            custom_id="application_selectmenu",
            placeholder="Wähle eine Rolle aus",
            max_values=len(options),
            *options
        )
        info_message = await channel.send(embed=setup_info_embed, components=role_info_select)
        application_message = await channel.send(embed=setup_application_embed, components=application_select)
        with open("data.json", "w") as f:
            json.dump({
                "channel_id": int(channel.id),
                "info_message_id": int(info_message.id),
                "application_message_id": int(application_message.id)
            }, f)
        await ctx.send("Setup erfolgreich!", ephemeral=True)

    @application.subcommand(
        sub_cmd_name="allow",
        sub_cmd_description="Erlaubt Bewerbungen"
    )
    @i.auto_defer()
    async def application_allow(self, ctx: i.SlashContext):
        with open("data.json", "r") as f:
            data = json.load(f)
        info_channel = await ctx.guild.fetch_channel(data["channel_id"])
        application_message = await info_channel.fetch_message(data["application_message_id"])

        application_select: i.StringSelectMenu = application_message.components[0].components[0]
        application_select.disabled = False
        await application_message.edit(components=[application_select])
        await ctx.send("Bewerbungen sind jetzt erlaubt!", ephemeral=True)

    @application.subcommand(
        sub_cmd_name="disallow",
        sub_cmd_description="Verbietet Bewerbungen"
    )
    @i.auto_defer()
    async def application_disallow(self, ctx: i.SlashContext):
        with open("data.json", "r") as f:
            data = json.load(f)
        info_channel = await ctx.guild.fetch_channel(data["channel_id"])
        application_message = await info_channel.fetch_message(data["application_message_id"])

        application_select: i.StringSelectMenu = application_message.components[0].components[0]
        application_select.disabled = True
        await application_message.edit(components=[application_select])
        await ctx.send("Bewerbungen sind jetzt verboten!", ephemeral=True)

    @i.slash_command(
        name="roles",
        description="Basis Command für die Rollen der Bewerbung",
        scopes=scope_ids
    )
    async def roles(self, ctx: i.SlashContext):
        pass

    @roles.subcommand(
        sub_cmd_name="enable",
        sub_cmd_description="Aktiviert eine Rolle für die Bewerbung",
    )
    @i.auto_defer()
    async def role_enable(self, ctx: i.SlashContext):
        options, selectmenus = [], []
        selectmenu_count = 0
        for role in ctx.guild.roles:
            self.cur.execute(
                "SELECT role_id FROM roles WHERE role_id = ?", (int(role.id),))
            if self.cur.fetchone() is not None:
                continue
            options.append(i.StringSelectOption(
                label=role.name,
                value=str(role.id)
            ))
            if len(options) == 25:
                selectmenus.append(i.StringSelectMenu(
                    custom_id=f"role_enable_selectmenu{selectmenu_count + 1}",
                    placeholder="Wähle eine Rolle aus",
                    max_values=len(options),
                    *options
                ))
                options = []
                selectmenu_count += 1
                if selectmenu_count == 3:
                    break
        if len(options) > 0 and selectmenu_count < 3:
            selectmenus.append(i.StringSelectMenu(
                custom_id=f"role_enable_selectmenu{selectmenu_count + 1}",
                placeholder="Wähle eine Rolle aus",
                max_values=len(options),
                *options
            ))
        await ctx.send("Wähle die Rollen aus, die aktiviert werden sollen.")
        for selectmenu in selectmenus:
            await ctx.channel.send(components=selectmenu, silent=True)

    @roles.subcommand(
        sub_cmd_name="disable",
        sub_cmd_description="Deaktiviert eine Rolle für die Bewerbung",
    )
    async def role_disable(self, ctx: i.SlashContext):
        options = []
        self.cur.execute("SELECT role_id, name FROM roles WHERE enabled = 1")
        for role_id, name in self.cur.fetchall():
            options.append(i.StringSelectOption(
                label=name,
                value=str(role_id)
            ))
        role_select_menu = i.StringSelectMenu(
            custom_id="role_disable_selectmenu",
            placeholder="Wähle eine Rolle aus",
            max_values=len(options),
            *options
        )
        await ctx.send("Wähle die Rollen aus, die deaktiviert werden sollen.",
                       components=role_select_menu, ephemeral=True)

    @roles.subcommand(
        sub_cmd_name="edit",
        sub_cmd_description="Editiert eine Rolle"
    )
    async def role_edit(self, ctx: i.SlashContext):
        self.cur.execute("SELECT role_id, name FROM roles")
        options = []
        for role_id, name in self.cur.fetchall():
            options.append(i.StringSelectOption(
                label=name,
                value=str(role_id)
            ))
        role_select_menu = i.StringSelectMenu(
            custom_id="role_edit_selectmenu",
            placeholder="Wähle eine Rolle aus",
            *options
        )
        await ctx.send("Wähle die Rollen aus, die editiert werden sollen.",
                       components=role_select_menu, ephemeral=True)

    @roles.subcommand(
        sub_cmd_name="delete",
        sub_cmd_description="Löscht eine Rolle"
    )
    async def role_delete(self, ctx: i.SlashContext):
        self.cur.execute("SELECT role_id, name FROM roles")
        options = []
        for role_id, name in self.cur.fetchall():
            options.append(i.StringSelectOption(
                label=name,
                value=str(role_id)
            ))
        role_select_menu = i.StringSelectMenu(
            custom_id="role_delete_selectmenu",
            placeholder="Wähle eine Rolle aus",
            min_values=1,
            max_values=len(options),
            *options
        )
        await ctx.send("Wähle die Rollen aus, die gelöscht werden sollen.",
                       components=role_select_menu, ephemeral=True)

    @i.component_callback("role_enable_selectmenu1")
    @i.auto_defer()
    async def role_enable_callback1(self, ctx: i.ComponentContext):
        await ctx.send("Die Rollen werden aktiviert.", ephemeral=True)
        await self._enable_roles(ctx)

    @i.component_callback("role_enable_selectmenu2")
    @i.auto_defer()
    async def role_enable_callback2(self, ctx: i.ComponentContext):
        await ctx.send("Die Rollen werden aktiviert.", ephemeral=True)
        await self._enable_roles(ctx)

    @i.component_callback("role_enable_selectmenu3")
    @i.auto_defer()
    async def role_enable_callback3(self, ctx: i.ComponentContext):
        await ctx.send("Die Rollen werden aktiviert.", ephemeral=True)
        await self._enable_roles(ctx)

    @i.component_callback("role_disable_selectmenu")
    @i.auto_defer()
    async def role_disable_callback(self, ctx: i.ComponentContext):
        for role in ctx.values:
            self.cur.execute(
                "UPDATE roles SET enabled = 0 WHERE role_id = ?", (int(role),))
            self.con.commit()
        await self.update_menus(ctx.guild)
        await ctx.edit_origin(content="Rollen erfolgreich deaktiviert!", components=[])

    @i.component_callback("role_edit_selectmenu")
    @i.auto_defer()
    async def role_edit_callback(self, ctx: i.ComponentContext):
        self.cur.execute("""SELECT name, short_description, long_description FROM roles WHERE role_id = ?""",
                         (int(ctx.values[0]),))
        name, short_description, long_description = self.cur.fetchone()
        components = [
            i.InputText(
                label="Name",
                style=i.TextStyles.SHORT,
                placeholder="Name der Rolle (normalerweise automatisch)",
                custom_id="role_edit_name",
                value=name
            ),
            i.InputText(
                label="Kurzbeschreibung",
                style=i.TextStyles.SHORT,
                placeholder="Kurzbeschreibung der Rolle",
                custom_id="role_edit_short_description",
                value=short_description
            ),
            i.InputText(
                label="Langbeschreibung",
                style=i.TextStyles.PARAGRAPH,
                placeholder="Langbeschreibung der Rolle",
                custom_id="role_edit_long_description",
                value=long_description
            )
        ]
        edit_modal = i.Modal(
            title="Rolle editieren",
            custom_id="role_edit_modal",
            *components
        )
        await ctx.send_modal(edit_modal)
        modal_ctx: i.ModalContext = await ctx.bot.wait_for_modal(edit_modal, ctx.user.id)
        self.cur.execute("""UPDATE roles SET name = ?, short_description = ?, long_description = ? WHERE role_id = ?""",
                         (modal_ctx.responses["role_edit_name"], modal_ctx.responses["role_edit_short_description"],
                          modal_ctx.responses["role_edit_long_description"], int(ctx.values[0])))
        self.con.commit()
        await self.update_menus(ctx.guild)
        await modal_ctx.send(content="Rolle erfolgreich editiert!", components=[], ephemeral=True)

    @i.component_callback("role_delete_selectmenu")
    @i.auto_defer()
    async def role_delete_callback(self, ctx: i.ComponentContext):
        for role in ctx.values:
            self.cur.execute("DELETE FROM roles WHERE role_id = ?", (int(role),))
            self.con.commit()
        await self.update_menus(ctx.guild)
        await ctx.edit_origin(content="Rollen erfolgreich gelöscht!", components=[])

    @i.component_callback("role_info_selectmenu")
    @i.auto_defer()
    async def role_info_callback(self, ctx: i.ComponentContext):
        if ctx.values[0] == "Kurzbeschreibung":
            self.cur.execute("SELECT role_id, short_description FROM roles")
            embeds = []
            for role_id, short_description in self.cur.fetchall():
                role = await ctx.guild.fetch_role(int(role_id))
                embeds.append(i.Embed(
                    title=role.name,
                    description=short_description,
                    color=i.RoleColors.DARK_BLUE.value,
                    thumbnail=i.EmbedAttachment(
                        url="https://cdn.discordapp.com/attachments/923199431447289916/923200094264774676/LogoDiscord.png"),
                ))
            paginator = Paginator.create_from_embeds(self.bot, *embeds, timeout=1800)
            paginator.show_select_menu = True
            await paginator.send(ctx, **{"ephemeral": True})
        elif len(ctx.values) == 1:
            self.cur.execute(
                "SELECT long_description FROM roles WHERE role_id = ?", (int(ctx.values[0]),))
            role = await ctx.guild.fetch_role(int(ctx.values[0]))
            role_info_embed = i.Embed(
                title=role.name,
                description=self.cur.fetchone()[0],
                color=i.RoleColors.DARK_BLUE.value,
                thumbnail=i.EmbedAttachment(
                    url="https://cdn.discordapp.com/attachments/923199431447289916/923200094264774676/LogoDiscord.png"),
            )
            await ctx.send(ephemeral=True, embed=role_info_embed)
        else:
            embeds = []
            for role_id in ctx.values:
                self.cur.execute(
                    "SELECT long_description FROM roles WHERE role_id = ?", (int(role_id),))
                role = await ctx.guild.fetch_role(int(role_id))
                embeds.append(i.Embed(
                    title=role.name,
                    description=self.cur.fetchone()[0],
                    color=i.RoleColors.DARK_BLUE.value,
                    thumbnail=i.EmbedAttachment(
                        url="https://cdn.discordapp.com/attachments/923199431447289916/923200094264774676/LogoDiscord.png"),
                ))
            paginator = Paginator.create_from_embeds(self.bot, *embeds, timeout=1800)
            paginator.show_select_menu = True
            await paginator.send(ctx, **{"ephemeral": True})

    @i.component_callback("application_selectmenu")
    async def role_application_callback(self, ctx: i.ComponentContext):
        components = [i.InputText(
            label="Bewerbung",
            style=i.TextStyles.PARAGRAPH,
            placeholder="Bitte schreibe hier deine Bewerbung. Du hast 10 Minuten Zeit.",
            custom_id="application_text_input",
            min_length=50
        )]
        application_text_modal = i.Modal(
            title="GIRC Bewerbung",
            custom_id="application_text_modal",
            *components
        )
        await ctx.send_modal(application_text_modal)
        try:
            modal_ctx: i.ModalContext = await ctx.bot.wait_for_modal(application_text_modal, ctx.user.id, timeout=600)
        except TimeoutError:
            await ctx.send("Zeitüberschreitung bei der Bewerbung.", ephemeral=True)
            return
        application_channel = await self.bot.fetch_channel(int(self.config["Channels"]["send_application_channel_id"]))
        role = await ctx.guild.fetch_role(int(ctx.values[0]))
        application_embed = i.Embed(
            title="GIRC Bewerbung",
            description=f"{ctx.user.mention} hat sich für die Rolle {role.name} beworben.",
            color=i.RoleColors.DARK_BLUE.value
        )
        application_embed.add_field(
            name="Bewerbungstext",
            value=modal_ctx.responses["application_text_input"]
        )
        await application_channel.send(embed=application_embed)
        await modal_ctx.send("Bewerbung erfolgreich abgeschickt! Wir bearbeiten diese so schnell wie möglich und melden uns dann bei dir.", ephemeral=True)


def setup(bot):
    ApplicationCommand(bot)
