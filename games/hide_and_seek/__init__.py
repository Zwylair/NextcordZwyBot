import nextcord
from nextcord.ext import commands
from settings import HAPPY_SQUAD_GUILD_ID, TEST_GUILD_ID
from games.hide_and_seek.lobby import HideAndSeekView


class HideNSeek(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='hide_and_seek', description='Create Hide&Seek lobby', guild_ids=[HAPPY_SQUAD_GUILD_ID, TEST_GUILD_ID])
    async def hide_and_seek(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title='Wait please', description='Wait please...')
        status_interaction = await interaction.send(embed=embed, ephemeral=True)

        view = HideAndSeekView(status_interaction, interaction.user)
        await view.update()
