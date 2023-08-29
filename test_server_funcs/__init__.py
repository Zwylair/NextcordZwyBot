import nextcord.ext.commands
import settings


class TestCommandsCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='guilds_info', description='Shows info of any guild where this bot involved', guild_ids=[settings.TEST_GUILD_ID])
    async def guilds_info(self, interaction: nextcord.Interaction):
        if interaction.user.id != settings.OWNER_ID:
            return

        embeds = []
        for i in self.bot.guilds:
            timestamp = i.created_at.timestamp()
            timestamp = f'{timestamp}'.split('.')[0]

            embed = nextcord.Embed(title=f'{i.name} [ID: {i.id}]',
                                   description=f'Desc: {"" if i.description is None else i.description}')
            embed.add_field(name='Info',
                            value=f'```Owner: {i.owner}\n'
                                  f'Members: {i.member_count}\n'
                                  f'    Bots: {len(i.bots)}\n'
                                  f'    Humans: {len(i.humans)}```')
            embed.add_field(name='Was created',
                            value=f'<t:{timestamp}:f>\n'
                                  f'<t:{timestamp}:R>')
            embed.set_thumbnail(i.icon.with_size(64).url)
            embeds.append(embed)

        await interaction.send(embeds=embeds, ephemeral=True)

    @nextcord.slash_command(name='eval', description='Eval', guild_ids=[settings.TEST_GUILD_ID])
    async def eval_cmd(self, interaction: nextcord.Interaction,
                       text_to_eval: str = nextcord.SlashOption(name='text_to_eval', description='text_to_eval', required=True)):
        if interaction.user.id != settings.OWNER_ID:
            return

        ret = eval(text_to_eval)
        await interaction.send(f'{ret}', ephemeral=True)

    # @nextcord.slash_command(name='test', description='test', guild_ids=[settings.TEST_GUILD_ID])
    # async def test(self, interaction: nextcord.Interaction):
    #   ...


def setup(bot):
    bot.add_cog(TestCommandsCog(bot))
