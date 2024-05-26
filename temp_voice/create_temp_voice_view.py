import nextcord.ext.commands
from temp_voice.setup_temp_voice import *


class CreatePrivateVoiceView(nextcord.ui.View):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @nextcord.ui.button(label='Создать приватный гс', style=nextcord.ButtonStyle.blurple)
    async def create_voice(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        msg = await interaction.send('...', ephemeral=True)
        view = SetupPrivateVoiceView(msg, interaction.user, self.bot)

        await msg.edit(view=view)
        await view.update_embed()
