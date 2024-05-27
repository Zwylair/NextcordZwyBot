import json
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
        fetch = cur.fetchone()

        cur.close()
        conn.close()

        if fetch is None:
            await interaction.send('Вы находитесь не в приватном канале!', ephemeral=True)
            return

        server_id, vc_channel_id, people_limit, allowed_members, delete_option = fetch
        allowed_members = [interaction.guild.get_member(i) for i in json.loads(allowed_members)]
        vc_channel = interaction.guild.get_channel(vc_channel_id)
        msg = await interaction.send('...', ephemeral=True)

        view = SetupPrivateVoiceView(msg, interaction.user, self.bot)
        view.vc_name = vc_channel.name
        view.author = allowed_members[0]
        view.people_limit = people_limit
        view.allowed_members = allowed_members
        view.delete_option = delete_option

        view = ModifyPrivateVoiceView(view, vc_channel, interaction)
        await msg.edit(view=view)
        await view.update_embed()
