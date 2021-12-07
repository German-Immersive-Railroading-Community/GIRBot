# GIRBot
The DC Bot for GIRC.

## .env File
Here is a template for a .env file. These are the variables you would need to specify:
```
token=<Insert your token here>

guild_id=690967067855421470
sent_app_channel_id=692405514700587039
sent_idea_channel_id=917813601794945058
builderwish_channel_id=810621723145797672

head_dev_role_id=814462429185835018
dev_role_id=709719558189088809
admin_role_id=690970811410153493
owner_role_id=690970413781614603

host=<IP of Database-Server>
db_user=<The user you want to acces the database with>
db_password=<The password for this user>
db_name=<The name of the database>
```
The IDs are freely available from Discord and are therefore clearly listed here.

## Database table setup

To understand the following tables that show how each database table is constructed, take a look of how the tables are structured:

| **column** |  column  |
|:----------:|:--------:|
|  datatype  | datatype |

Keep in mind that bold columns represent primary keys.

### Member table

| **id** | uuid |
|:------:|:----:|
| bigint | text |

### Application table

| **id** | member_id |  role  | message_id |
|:------:|:---------:|:------:|:----------:|
|  int   |  bigint   | bigint |   bigint   |

### app_vote table

| **app_id** | is_in_favor | voter_id |
|:----------:|:-----------:|:--------:|
|    int     |   tinyint   |  bigint  |