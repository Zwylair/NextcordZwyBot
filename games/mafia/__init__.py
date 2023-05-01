import nextcord.ext.commands
from games.mafia.lobby import MafiaLobbyView


class MafiaCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='mafia_create_lobby', description='Создать лобби игры "мафия"')
    async def create_mafia_lobby(self, interaction: nextcord.Interaction):
        status_interaction = await interaction.send('Processing', ephemeral=True)
        view = MafiaLobbyView(status_interaction, author=interaction.user)
    
        await view.update()
        await status_interaction.edit(view=view)
