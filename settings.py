from os import getenv

TOKEN = getenv('zwybot_dsbot_token')  # testbot_ds_token zwybot_dsbot_token
OWNER_ID = 911715617114042398
TEST_GUILD_ID = 988013282449309706
SQL_DB_PATH = 'db.sql'

REGISTRATION_BANNER_URL = 'https://media.tenor.com/ommRkBKPWAsAAAAC/anime.gif'
ERROR_BANNER_URL = 'https://64.media.tumblr.com/089c1e0701c82d16e9431831a2d57de8/ce1a77f2aa42090d-c5/s540x810/7667c312e8e796272d5ceb5b864f11f68c4c3e4a.gifv'
VERIFY_BANNER_URL = 'https://i.pinimg.com/originals/4c/16/22/4c16221bd6acb57eb0712d3ee6539fb8.png'
# MAFIA_BANNER_URL = 'https://russiaedu.ru/media/cache/image_md_resize/uploads/upload-images/2019/02/24/WvXkVtpWzjw.jpg'
# METACORE_GUILD_ID = 981167384872243210
# HAPPY_SQUAD_GUILD_ID = 1071576466078306495
# METACORE_EVENT_CHANNEL_ID = 1018281669666545765
# HAPPY_SQUAD_EVENT_CHANNEL_ID = 1072837026921074739
# EVENT_CREATOR_ROLE_ID = 1079842562732470312
# TEST_EVENT_CREATOR_ROLE_ID = 1025852955481612339
# TEST_METACORE_EVENT_CHANNEL_ID = 988013285288849450
# DATETIME_WEEKDAY_DICT = {
#     0: 'monday',
#     1: 'tuesday',
#     2: 'wednesday',
#     3: 'thursday',
#     4: 'friday',
#     5: 'saturday',
#     6: 'sunday'
# }
DB_CREATE_SEQUENCE = {
    'bot': "CREATE TABLE bot(user_id int)",
    'political': "CREATE TABLE political (name varchar(255), desc varchar(255), banner_url varchar(255), popularity int)",
    'verifier_emoji': "CREATE TABLE verifier_emoji (role_id bigint, message_id bigint)",
    'views': "CREATE TABLE views (view_type varchar(255), guild_id BIGINT, channel_id BIGINT, message_id BIGINT, role_id BIGINT)",
    'event_templates': "CREATE TABLE event_templates (server_id BIGINT, template_name varchar(255), embed_bytes varbinary(4096))"
}
