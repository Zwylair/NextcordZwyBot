import nextcord.ext.commands
import db
from funcs import *
from verifier.db import VerifierBaseEmbedView


class VerifierCogListener(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot
    
    @nextcord.ext.commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        if payload.emoji.name != '☑️':
            return

        conn = db.get_conn()
        cur = conn.cursor()

        cur.execute(f'SELECT role_id FROM verifier_emoji WHERE message_id = ?', (payload.message_id,))
        result = cur.fetchone()

        if not await is_role_exist(self.bot, payload.guild_id, result[0]):
            view_guild = self.bot.get_guild(payload.guild_id)
            view_chat = view_guild.get_channel(payload.channel_id)
            view_message = await view_chat.fetch_message(payload.message_id)
            view_embed = view_message.embeds[0]

            view_embed.set_footer(
                text='Верификация остановила свою работу из-за отсутствие выдаваемой роли. '
                     'Для решения - пересоздайте сообщение верификации с новой ролью'
            )

            cur.execute(f'DELETE FROM verifier_emoji WHERE message_id = ?', (payload.message_id,))
            conn.commit()
            return

        cur.close()
        conn.close()
        await payload.member.add_roles(payload.member.guild.get_role(result[0]))


class VerifierEmbedEmojiView(VerifierBaseEmbedView):
    @nextcord.ui.button(label='📨', style=nextcord.ButtonStyle.green)
    async def send_button_callback(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.give_role is None:
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Вы не указали выдаваемую роль!')
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return

        self.out_embed.remove_field(0)

        conn = db.get_conn()
        cur = conn.cursor()

        msg = await self.out_chat.send(embed=self.out_embed)
        await msg.add_reaction('☑️')

        cur.execute(f"INSERT INTO verifier_emoji (role_id, message_id) VALUES ('{self.give_role.id}', '{msg.id}')")
        conn.commit()
        cur.close()
        conn.close()

        await self.embed_message.delete()
        await interaction.send('Сообщение отправлено!', ephemeral=True)
