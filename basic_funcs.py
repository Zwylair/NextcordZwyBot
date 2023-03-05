from string import ascii_lowercase, digits
import random
import nextcord
from nextcord.ext.commands import Bot


async def is_message_exist(bot: Bot, guild_id: int, channel_id: int, message_id: int) -> bool:
    try:
        await bot.get_guild(guild_id).get_channel(channel_id).fetch_message(message_id)
    except (nextcord.NotFound, AttributeError):  # AttributeError raises when guild or channel is None
        return False
    return True


async def is_role_exist(bot: Bot, guild_id: int, role_id: int) -> bool:
    return False if bot.get_guild(guild_id).get_role(role_id) is None else True


async def gen_rand_str(length: int) -> str:
    out = ''
    for _ in range(length):
        if random.randint(1, 6) < 3:
            out += random.choice(ascii_lowercase)
        else:
            out += random.choice(digits)
    return out
