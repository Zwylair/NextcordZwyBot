from os import getenv

TOKEN = getenv('zwybot_dsbot_token')  # testbot_ds_token zwybot_dsbot_token
OWNER_ID = 911715617114042398
TEST_GUILD_ID = 988013282449309706
SQL_DB_PATH = 'db.sql'
REGISTRATION_BANNER_URL = 'https://media.tenor.com/ommRkBKPWAsAAAAC/anime.gif'
ERROR_BANNER_URL = 'https://64.media.tumblr.com/089c1e0701c82d16e9431831a2d57de8/ce1a77f2aa42090d-c5/s540x810/7667c312e8e796272d5ceb5b864f11f68c4c3e4a.gifv'
VERIFY_BANNER_URL = 'https://i.pinimg.com/originals/4c/16/22/4c16221bd6acb57eb0712d3ee6539fb8.png'
DATETIME_WEEKDAY_DICT = {
    0: 'monday',
    1: 'tuesday',
    2: 'wednesday',
    3: 'thursday',
    4: 'friday',
    5: 'saturday',
    6: 'sunday'
}
DB_DUMPS = (
    'CREATE TABLE bot(user_id INT)',
    'CREATE TABLE views(view_type TEXT, guild_id INT, channel_id INT, message_id INT, role_id INT)',
    'CREATE TABLE verifier_emoji(role_id INT, message_id INT)',
    'CREATE TABLE political(name TEXT, desc TEXT, banner_url TEXT, popularity INT)',
    'CREATE TABLE event_templates(server_id INT, template_name TEXT, embed_bytes BLOB)',
    'CREATE TABLE private_vc_config(server_id INT, vc_category INT)',
    'CREATE TABLE private_vc(server_id INT, vc_channel_id INT)'
)
