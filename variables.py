from decouple import config

sent_app_channel_id = int(config("sent_app_channel_id"))
builderwish_channel_id=int(config("builderwish_channel_id"))
sent_idea_channel_id=int(config("sent_idea_channel_id"))

guild_id = str(config("guild_id")).split(",")
guild_id = [int(i) for i in guild_id]
girc_guild_id = int(guild_id[0])

head_dev_role_id = int(config("head_dev_role_id"))
dev_role_id = int(config("dev_role_id"))
admin_role_id = int(config("admin_role_id"))
owner_role_id = int(config("owner_role_id"))
builder_role_id = int(config("builder_role_id"))
head_builder_role_id = int(config("head_builder_role_id"))
pr_role_id = int(config("pr_role_id"))
head_pr_user_id = int(config("head_pr_user_id"))

count_head_dev = int(config("count_head_dev"))
count_head_builder = int(config("count_head_builder"))

head_voters = {
    dev_role_id : [head_dev_role_id, count_head_dev],
    builder_role_id : [head_builder_role_id, count_head_builder],
    pr_role_id : head_pr_user_id
}

token = config("token")
bot_prefix = "ANiceAndLongPrefixSoNoOneUsesIt"
