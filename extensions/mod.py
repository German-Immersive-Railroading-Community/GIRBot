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
        audit_log = await event.message.guild.fetch_audit_log(action_type=AuditLogEventType.MESSAGE_DELETE, limit=3)
        deleted_by = ""
        for entry in audit_log.entries:
            try:
                if int(entry.user_id) == int(event.message.author.id):
                    break
                elif int(entry.target_id) == int(event.message.author.id):
                    member = await event.message.guild.fetch_member(entry.user_id)
                    deleted_by = " von " + member.mention
                    break
            except:
                continue

        formatted_time = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
        message_author_name = event.message.author.nickname
        log_channel = await self.client.fetch_channel(self.log_channel_id)
        embed = i.Embed(
            title=message_author_name,
            description=f"Nachricht in <#{str(event.message.channel.id)}>{deleted_by} gelöscht.",
            color=0xFF0000,
            footer=i.EmbedFooter(text=formatted_time)
        )
        embed.add_field(name="Nachricht",
                        value=event.message.content)
        await log_channel.send(embed=embed)  # type: ignore

    @i.listen(MessageUpdate)
    async def on_message_update(self, event: MessageUpdate):
        if event.before.content == event.after.content:
            return
        formatted_time = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
        message_author_name = event.before.author.display_name
        log_channel = await self.client.fetch_channel(self.log_channel_id)
        embed = i.Embed(
            title=message_author_name,
            description=f"Nachricht in <#{str(event.before.channel.id)}> editiert.",
            color=0xebc400,
            footer=i.EmbedFooter(text=formatted_time)
        )
        embed.add_field(name="Vorher",
                        value=event.before.content)
        embed.add_field(name="Nachher",
                        value=event.after.content)
        await log_channel.send(embed=embed)  # type: ignore
