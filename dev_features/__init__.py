import io
import re
import nextcord.ext.commands
import funcs
from settings import *


class DevFeaturesCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name='guilds_info',
        description='Shows information about any guild that this bot participates in',
        guild_ids=[TEST_GUILD_ID]
    )
    async def guilds_info(self, interaction: nextcord.Interaction):
        if interaction.user.id != OWNER_ID:
            return

        embeds = []
        for guild in self.bot.guilds[:10]:
            storage = io.BytesIO()
            await guild.icon.with_size(128).save(storage)
            timestamp = guild.created_at.timestamp()
            timestamp = f'{timestamp}'.split('.')[0]  # remove unnecessary trash after dot (123123123.489734)

            storage.seek(0)
            average_color = await funcs.get_average_color(storage)
            average_color = nextcord.Color.from_rgb(average_color[0], average_color[1], average_color[2])

            embed = nextcord.Embed(
                title=f'{guild.name} [ID: {guild.id}]',
                description=None
            )
            embed.add_field(
                name='Info',
                value=f'```Owner: {guild.owner}\n'
                      f'Members: {guild.member_count}\n'
                      f' ╠═Bots: {len(guild.bots)}\n'
                      f' ╚═Humans: {len(guild.humans)}```'
            )
            embed.add_field(
                name='Was created',
                value=f'<t:{timestamp}:f>\n'
                      f'<t:{timestamp}:R>'
            )
            embed.set_thumbnail(guild.icon.with_size(128).url)
            embed.colour = average_color
            embeds.append(embed)

        await interaction.send(embeds=embeds, ephemeral=True)

    @nextcord.slash_command(name='extract_emojis', description='Extract emoji\'s webhook tag', guild_ids=[TEST_GUILD_ID])
    async def extract_emojis(
        self, interaction: nextcord.Interaction,
        message_url: str = nextcord.SlashOption(
            name='message_url',
            description='Link to the message with emojis'
        )
    ):
        if interaction.user.id != OWNER_ID:
            return

        # ['https:', '', 'discord.com', 'channels', '{server_id}', '{channel_id}', '{message_id}']
        match message_url.split('/'):
            case ['https:', '', 'discord.com', 'channels', _, channel_id, message_id, *_]:
                # Get input message content
                try:
                    channel = self.bot.get_channel(int(channel_id))
                    msg = await channel.fetch_message(int(message_id))
                except (nextcord.NotFound, nextcord.Forbidden):
                    embed = nextcord.Embed(
                        title='Ошибка! :stop_sign:', colour=0xEC0D6D,
                        description='Неверная ссылка на сообщение / Данное сообщение не найдено!'
                    )
                    await interaction.send(embed=embed, ephemeral=True)
                    return
                else:
                    emojis = re.findall(EMOJI_REGEX, msg.content)
                    embed = nextcord.Embed(title='Emojis', colour=0xFFFFFF)

                    for i in emojis:
                        animated, name, emoji_id = i
                        raw_emoji = f'<{animated}:{name}:{emoji_id}>'
                        embed.add_field(name=raw_emoji, value=f'`{raw_emoji}`')

                    await interaction.send(embed=embed, ephemeral=True)
                    return
            case _:
                embed = nextcord.Embed(
                    title='Ошибка! :stop_sign:', colour=0xEC0D6D,
                    description='Неверная ссылка на сообщение / Данное сообщение не найдено!'
                )
                await interaction.send(embed=embed, ephemeral=True)

    # @nextcord.slash_command(name='test', description='test', guild_ids=[settings.TEST_GUILD_ID])
    # async def test(self, interaction: nextcord.Interaction):
    #   ...


def setup(bot):
    bot.add_cog(DevFeaturesCog(bot))
