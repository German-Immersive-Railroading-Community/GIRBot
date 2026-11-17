import configparser as cp
import time

import interactions as i
from interactions.api.events import MessageDelete, MessageUpdate
from interactions.models.discord import AuditLogEventType

scope_ids = []


class ModCommand(i.Extension):
    def __init__(self, client: i.Client) -> None:
        self.client = client
        self.refresh_config()

    def refresh_config(self):
        config = cp.ConfigParser()
        config.read("config.ini")
        global scope_ids
        scope_ids = config.get('General', 'scope_ids').split(',')
        self.log_channel_id = config.getint('Mod', 'log_channel_id')

    @i.listen(MessageDelete)
    async def on_message_delete(self, event: MessageDelete):
        if event.message is None or event.message.guild is None:
            return

        deleted_by = ""

        try:
            audit_log = await event.message.guild.fetch_audit_log(
                action_type=AuditLogEventType.MESSAGE_DELETE,
                limit=3
            )

            for entry in audit_log.entries:
                try:
                    if int(entry.user_id) == int(event.message.author.id):
                        break
                    elif int(entry.target_id) == int(event.message.author.id):
                        member = await event.message.guild.fetch_member(entry.user_id)
                        deleted_by = " von " + member.mention
                        break
                except (TypeError, ValueError, AttributeError):
                    continue

        except Exception:
            logging.getLogger("bot").exception(
                "Audit-Log konnte nicht abgerufen werden."
            )

        formatted_time = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())

        message_author_name = (
            getattr(event.message.author, "display_name", None)
            or getattr(event.message.author, "username", None)
            or "Unbekannt"
        )

        log_channel = await self.client.fetch_channel(self.log_channel_id)

        message_content = event.message.content or "[Kein Textinhalt – möglicherweise Embed oder Anhang]"

        embed = i.Embed(
            title=message_author_name,
            description=f"Nachricht in <#{event.message.channel.id}>{deleted_by} gelöscht.",
            color=0xFF0000,
            footer=i.EmbedFooter(text=formatted_time)
        )

        embed.add_field(
            name="Nachricht",
            value=message_content[:1021] + "..." if len(message_content) > 1024 else message_content,
            inline=False
        )

        await log_channel.send(embed=embed)

    @i.listen(MessageUpdate)
    async def on_message_update(self, event: MessageUpdate):
        if event.before is None or event.after is None:
            return
        if event.before.content == event.after.content:
            return
        formatted_time = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
        message_author_name = event.before.author.display_name
        log_channel = await self.client.fetch_channel(self.log_channel_id)
        before_content = event.before.content or "[Kein Textinhalt]"
        after_content = event.after.content or "[Kein Textinhalt]"
        embed = i.Embed(
            title=message_author_name,
            description=f"Nachricht in <#{str(event.before.channel.id)}> editiert.",
            color=0xebc400,
            footer=i.EmbedFooter(text=formatted_time)
        )
        embed.add_field(
            name="Vorher",
            value=before_content[:1021] + "..." if len(before_content) > 1024 else before_content,
            inline=False
        )

        embed.add_field(
            name="Nachher",
            value=after_content[:1021] + "..." if len(after_content) > 1024 else after_content,
            inline=False
        )
        await log_channel.send(embed=embed)  # type: ignore
