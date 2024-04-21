import random
import nextcord.ext.commands


class FuncsCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='dice', description='Бросить кубики')
    async def dice(
            self, interaction: nextcord.Interaction,
            count: int = nextcord.SlashOption(
                name='count', required=False,
                description='Количество кубиков'
            )
    ):
        count = 1 if count is None else count
        dice_numbs = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}
        embed = nextcord.Embed(title='Игровые кости 🎲', description='Выпало число...', colour=0x80a4d4)

        for i in range(count):
            rand = random.randint(1, 6)
            embed.add_field(name=f'``Бросок №{i + 1}``', value=f'```Выпало {dice_numbs[rand]} ({rand})!```')
        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(FuncsCog(bot))
