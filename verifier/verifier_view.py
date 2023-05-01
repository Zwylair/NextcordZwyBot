import sqlite3
import nextcord
from verifier.db import VerifierBaseEmbedView


class VerifierView(nextcord.ui.View):
    def __init__(self, role: nextcord.Role | None):
        super(VerifierView, self).__init__(timeout=None)
        self.role = role

    async def is_role_still_existing(self, guild: nextcord.Guild):
        if self.role is None:
            return False
        print(guild.get_role(self.role.id))
        return False if guild.get_role(self.role.id) is None else True

    @nextcord.ui.button(label='✅', style=nextcord.ButtonStyle.green, custom_id='verification')
    async def verify(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if await self.is_role_still_existing(interaction.guild):
            await interaction.user.add_roles(self.role)
            await interaction.send('Роль выдана!', ephemeral=True)
        else:
            embed = interaction.message.embeds[0]
            embed.set_footer(text='Верификация остановила свою работу из-за отсутствие выдаваемой роли. Для решения - пересоздайте сообщение верификации с новой ролью')
            
            await interaction.message.edit(embed=embed)


class VerifierEmbedView(VerifierBaseEmbedView):
    @nextcord.ui.button(label='📨', style=nextcord.ButtonStyle.green)
    async def send_button_callback(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.give_role is None:
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Вы не указали выдаваемую роль!')
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return
        
        self.out_embed.remove_field(0)

        sql = sqlite3.connect('db.sql')
        view = VerifierView(self.give_role)
        msg = await self.out_chat.send(embed=self.out_embed, view=view)
        
        sql.execute(f"INSERT INTO views (view_type, guild_id, channel_id, message_id, role_id) VALUES ('verifier_view', '{self.out_chat.guild.id}', '{self.out_chat.id}', '{msg.id}', '{self.give_role.id}')")
        sql.commit()
        sql.close()

        await interaction.send('Сообщение отправлено!', ephemeral=True)
        await self.embed_message.delete()
