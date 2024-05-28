import nextcord.ext.commands
from temp_voice.setup_temp_voice import SetupPrivateVoiceView
from temp_voice.setup_temp_voice.modify_temp_voice import ModifyPrivateVoiceView
import db


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

    @nextcord.ui.button(label='Настройки текущего приватного гс')
    async def modify_voice(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.voice is None:
            await interaction.send('Вы не находитесь в приватном канале!', ephemeral=True)
            return

        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM private_vc WHERE server_id=? AND vc_channel_id=?',
            (interaction.user.guild.id, interaction.user.voice.channel.id)
        )
        res = cur.fetchone()
        cur.close()
        conn.close()

        if res is None:
            await interaction.send('Вы находитесь не в приватном канале!', ephemeral=True)
            return

        vc_channel = interaction.guild.get_channel(interaction.user.voice.channel.id)
        msg = await interaction.send('...', ephemeral=True)
        view = SetupPrivateVoiceView(msg, interaction.user, self.bot)
        view = ModifyPrivateVoiceView(view, vc_channel, interaction)

        await msg.edit(view=view)
        await view.update_embed()
