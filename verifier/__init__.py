import typing
import nextcord.ext.commands
import funcs
import settings
import verifier.verifier_view
import verifier.verifier_emoji
import verifier.classes
import verifier.db


class VerifierCog(nextcord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name='verifier', description='Создать сообщение верификации')
    async def verifier(
            self, interaction: nextcord.Interaction,
            target_chat: nextcord.TextChannel = nextcord.SlashOption(
                name='target_chat', required=True,
                description='Чат, в который будет отослано сообщение',
            ),
            verification_type: typing.Literal['button', 'emoji'] = nextcord.SlashOption(
                name='verification_type', required=True,
                description='Тип верификации',
            )
    ):
        if not await funcs.check_for_administrator_perm(interaction):
            return

        embed = nextcord.Embed(title='Title', colour=0x9a72ba, description='Basic Description')
        embed.set_image(settings.VERIFY_BANNER_URL)
        embed_message = await interaction.send(content='Предпоказ сообщения', embed=embed)

        match verification_type:
            case 'button':
                await embed_message.edit(
                    embed=embed,
                    view=verifier.verifier_view.VerifierEmbedView(
                        bot=self.bot,
                        base_interaction=interaction,
                        embed_message=embed_message,
                        out_embed=embed,
                        out_chat=target_chat)
                )
            case 'emoji':
                await embed_message.edit(
                    embed=embed,
                    view=verifier.verifier_emoji.VerifierEmbedEmojiView(
                        bot=self.bot,
                        base_interaction=interaction,
                        embed_message=embed_message,
                        out_embed=embed, out_chat=target_chat)
                )


def setup(bot):
    bot.add_cog(verifier.verifier_emoji.VerifierCogListener(bot))
    bot.add_cog(verifier.VerifierCog(bot))
