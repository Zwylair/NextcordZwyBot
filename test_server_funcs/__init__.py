import io

import nextcord.ext.commands

import funcs
import settings


class TestCommandsCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='guilds_info', description='Shows information about any guild that this bot participates in', guild_ids=[settings.TEST_GUILD_ID])
    async def guilds_info(self, interaction: nextcord.Interaction):
        if interaction.user.id != settings.OWNER_ID:
            return

        embeds = []
        for guild in self.bot.guilds[:10]:
            storage = io.BytesIO()
            await guild.icon.with_size(128).save(storage)
            timestamp = guild.created_at.timestamp()
            timestamp = f'{timestamp}'.split('.')[0]  # remove unnecessary trash after dot (123123123.489734)

            storage.seek(0)

            embed = nextcord.Embed(
                title=f'{guild.name} [ID: {guild.id}]',
                description=None
            )
            embed.add_field(
                name='Info',
                value=f'```Owner: {guild.owner}\n'
                      f'Members: {guild.member_count}\n'
                      f'  ╠═Bots: {len(guild.bots)}\n'
                      f'  ╚═Humans: {len(guild.humans)}```'
            )
            embed.add_field(
                name='Was created',
                value=f'<t:{timestamp}:f>\n'
                      f'<t:{timestamp}:R>'
            )
            embed.set_thumbnail(guild.icon.with_size(128).url)
            embed.colour = await funcs.get_average_color(storage)
            embeds.append(embed)

        await interaction.send(embeds=embeds, ephemeral=True)

    # @nextcord.slash_command(name='test', description='test', guild_ids=[settings.TEST_GUILD_ID])
    # async def test(self, interaction: nextcord.Interaction):
    #   ...


def setup(bot):
    bot.add_cog(TestCommandsCog(bot))
