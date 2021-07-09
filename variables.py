from decouple import config

sent_app_channel_id = config("sent_app_channel_id")

guild_id = str(config("guild_id")).split(",")
guild_id = [int(i) for i in guild_id]
girc_guild_id = int(guild_id[0])

head_dev_role_id = int(config("head_dev_role_id"))
dev_role_id = int(config("dev_role_id"))
admin_role_id = int(config("admin_role_id"))
owner_role_id = int(config("owner_role_id"))

token = config("token")
bot_prefix = "ANiceAndLongPrefixSoNoOneUsesIt"
