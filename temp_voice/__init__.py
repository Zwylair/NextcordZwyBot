from temp_voice.create_temp_voice_view import *
from temp_voice.listener import *
import nextcord.ext.commands


class TempVoiceCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='private_voice', description='private_voice')
    async def private_voice(self, _: nextcord.Interaction):
        pass

    @private_voice.subcommand(name='setup', description='Настроить создание приватных каналов')
    async def setup(
        self, interaction: nextcord.Interaction,
        private_vc_category: nextcord.CategoryChannel = nextcord.SlashOption(
            name='category',
            description='Категория, в которой будут создаваться приватные гс'
        )
    ):
        conn = db.get_conn()
        conn.execute(
            'INSERT INTO private_vc_config VALUES (?, ?)',
            (interaction.guild_id, private_vc_category.id)
        )
        conn.commit()
        conn.close()

        await interaction.send('Категория сохранена!', ephemeral=True)

    @private_voice.subcommand(name='send_creator', description='Отправить в чат создавалку приватных гс')
    async def send_private_voice_creator(
        self, interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(
            name='channel',
            description='Чат назначения'
        )
    ):
        embed = nextcord.Embed(
            title='Панель приватного гс',
            description='Нажимая эту кнопку вам откроется опции вашего приватного гс!',
            color=0xFFFFFF
        )
        msg = await channel.send(embed=embed, view=CreatePrivateVoiceView(self.bot))

        conn = db.get_conn()
        conn.execute(
            'INSERT INTO views VALUES (?, ?, ?, ?, ?)',
            ('create_temp_voice_view', interaction.guild_id, channel.id, msg.id, None)
        )
        conn.commit()
        conn.close()

        await interaction.send('Отправлено!', ephemeral=True)


def setup(bot):
    bot.add_cog(TempVoiceCog(bot))
