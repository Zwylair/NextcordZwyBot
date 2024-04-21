import io
import nextcord
from nextcord.ext.commands import Bot
from PIL import Image


async def is_message_exist(bot: Bot, guild_id: int, channel_id: int, message_id: int) -> bool:
    try:
        await bot.get_guild(guild_id).get_channel(channel_id).fetch_message(message_id)
    except (nextcord.NotFound, AttributeError):  # AttributeError raises when guild or channel is None
        return False
    return True


async def is_role_exist(bot: Bot, guild_id: int, role_id: int) -> bool:
    return False if bot.get_guild(guild_id).get_role(role_id) is None else True


async def check_for_administrator_perm(interaction: nextcord.Interaction) -> bool:
    for i in interaction.user.roles:
        if i.permissions.administrator:
            return True
    else:
        await interaction.send('Недостаточно прав! (Администратор)', ephemeral=True)
        return False


async def make_pastel_color(rgb_tuple, factor=0.5):
    """Make a pastel color from an RGB color tuple."""
    r, g, b = rgb_tuple
    # Calculate the pastel color by mixing the color with white
    pastel_r = int(r + (255 - r) * factor)
    pastel_g = int(g + (255 - g) * factor)
    pastel_b = int(b + (255 - b) * factor)

    return pastel_r, pastel_g, pastel_b


async def get_average_color(io_storage: io.BytesIO) -> nextcord.Color:
    img = Image.open(io_storage)
    img = img.convert("RGBA")
    width, height = img.size
    pixel_data = img.load()

    r_total = 0
    g_total = 0
    b_total = 0
    total_pixels = width * height

    for y in range(height):
        for x in range(width):
            r, g, b, _ = pixel_data[x, y]
            r_total += r
            g_total += g
            b_total += b

    average_color = (
        int(r_total / total_pixels),
        int(g_total / total_pixels),
        int(b_total / total_pixels)
    )

    r, g, b = await make_pastel_color(average_color, factor=0.1)
    return nextcord.Color(int('{:02x}{:02x}{:02x}'.format(r, g, b), 16))
