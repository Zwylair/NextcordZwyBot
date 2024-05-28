from temp_voice.create_temp_voice_view import *
import temp_voice.delete_vc_listener
import temp_voice.create_vc_listener
import nextcord.ext.commands


class TempVoiceCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='private_voice', description='private_voice')
    async def private_voice(self, _: nextcord.Interaction):
        pass

    @private_voice.subcommand(name='setup', description='Создать категорию и канал-создатель приватных комнат')
    async def setup(self, interaction: nextcord.Interaction):
        has_administrator = False
        for role in interaction.user.roles:
            if role.permissions.administrator:
                has_administrator = True
                break

        if interaction.user.guild.owner_id == interaction.user.id:
            has_administrator = True

        if not has_administrator:
            await interaction.send('У вас недостаточно прав (Администратор) для использования этой команды!', ephemeral=True)
            return

        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute(
            'SELECT creator_vc_channel FROM private_vc_server_config WHERE server_id=?',
            (interaction.guild_id,)
        )

        creator_vc_channel = cur.fetchone()
        if creator_vc_channel is not None:
            creator_vc_channel = creator_vc_channel[0]

        creator_vc: nextcord.VoiceChannel | None = interaction.guild.get_channel(creator_vc_channel)
        vc_category_permissions = nextcord.PermissionOverwrite(
            speak=False,
            stream=False,
            start_embedded_activities=False
        )
        if creator_vc is None:
            vc_category = await interaction.guild.create_category(
                'PRIVATE VOICE',
                reason='saved voice category was deleted'
            )
            creator_vc = await vc_category.create_voice_channel(
                'Create private VC',
                reason='saved voice category was deleted',
                overwrites={interaction.guild.default_role: vc_category_permissions}
            )

            conn = db.get_conn()
            conn.execute(
                'INSERT INTO private_vc_server_config VALUES (?, ?, ?)',
                (interaction.guild_id, vc_category.id, creator_vc.id)
            )
            conn.commit()
            conn.close()

            await interaction.send('Категория и канал-создатель приватных комнат созданы!', ephemeral=True)
            return
        await interaction.send('Категория и канал-создатель приватных комнат уже созданы!', ephemeral=True)

    @private_voice.subcommand(name='send_creator', description='Отправить в чат создавалку приватных гс')
    async def send_private_voice_creator(
        self, interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(
            name='channel',
            description='Чат назначения'
        )
    ):
        has_administrator = False
        for role in interaction.user.roles:
            if role.permissions.administrator:
                has_administrator = True
                break

        if interaction.user.guild.owner_id == interaction.user.id:
            has_administrator = True

        if not has_administrator:
            await interaction.send('У вас недостаточно прав (Администратор) для использования этой команды!', ephemeral=True)
            return

        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute(
            'SELECT server_id FROM private_vc_server_config WHERE server_id=?',
            (interaction.guild_id, )
        )
        res = cur.fetchone()

        if res is None:
            await interaction.send('Создание приватных гс не было настроено! Введите команду `/private_voice setup` для настройки', ephemeral=True)
            cur.close()
            conn.close()
            return

        embed = nextcord.Embed(
            title='Панель приватного гс',
            description='Нажимая эту кнопку вам откроется опции вашего приватного гс!',
            color=0xFFFFFF
        )
        msg = await channel.send(embed=embed, view=CreatePrivateVoiceView(self.bot))

        cur.execute(
            'INSERT INTO views VALUES (?, ?, ?, ?, ?)',
            ('create_temp_voice_view', interaction.guild_id, channel.id, msg.id, None)
        )
        conn.commit()
        cur.close()
        conn.close()

        await interaction.send('Отправлено!', ephemeral=True)


def setup(bot: nextcord.ext.commands.Bot):
    bot.add_cog(TempVoiceCog(bot))
    bot.add_listener(create_vc_listener.on_voice_state_update)
    bot.add_listener(delete_vc_listener.on_voice_state_update)
