import typing
import nextcord.ext.commands
import basic_funcs
import settings

import verifier.verifier_view
import verifier.verifier_emoji
import verifier.errors
import verifier.db


class VerifierCog(nextcord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='verifier', description='Создать сообщение верификации')
    async def verifier(self, interaction: nextcord.Interaction,
                       target_chat: nextcord.TextChannel = nextcord.SlashOption(name='target_chat',
                                                                                description='Чат, в который будет отослано сообщение',
                                                                                required=True),
                       verification_type: typing.Literal['button', 'emoji'] = nextcord.SlashOption(name='verification_type',
                                                                                                   description='Тип верификации',
                                                                                                   required=True)):
        if not await basic_funcs.check_for_administrator_perm(interaction):
            return
        
        verification_type = 'view' if verification_type == 'button' else verification_type
        embed = nextcord.Embed(title='Title', colour=0x9a72ba, description='Basic Description')
        embed.set_image(settings.VERIFY_BANNER_URL)
        
        embed_message = await interaction.send(content='Предпоказ сообщения', embed=embed)
        
        match verification_type:
            case 'view':
                await embed_message.edit(embed=embed,
                                         view=verifier.verifier_view.VerifierEmbedView(bot=self.bot, base_interaction=interaction,
                                                                                       embed_message=embed_message, out_embed=embed,
                                                                                       out_chat=target_chat))
            case 'emoji':
                await embed_message.edit(embed=embed,
                                         view=verifier.verifier_emoji.VerifierEmbedEmojiView(bot=self.bot, base_interaction=interaction,
                                                                                             embed_message=embed_message,
                                                                                             out_embed=embed, out_chat=target_chat))
    
