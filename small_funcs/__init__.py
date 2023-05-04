import random
import nextcord.ext.commands
import openai
import settings

openai.api_key = settings.OPENAI_API_KEY


class ChatGPTCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    # @nextcord.slash_command(name='gpt_says', description='Задать вопрос chat-gpt', guild_ids=[settings.METACORE_GUILD_ID, settings.TEST_GUILD_ID])
    # async def gpt_says(self, interaction: nextcord.Interaction,
    #                    prompt: str = nextcord.SlashOption(name='prompt', description='Вопрос для chatgpt', required=True)):
    #     # Chat-GPT's solution :)
    #     r = random.randint(64, 191)
    #     g = random.randint(64, 191)
    #     b = random.randint(64, 191)
    #
    #     random_pastel_hex_colour = (r << 16) + (g << 8) + b
    #
    #     await interaction.response.defer()
    #
    #     response = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[{'role': 'user', 'content': prompt}]
    #     )
    #
    #     response = response.choices[0].message.content
    #     response = response.lstrip('\n')
    #
    #     embed = nextcord.Embed(title=f'>>> {prompt}', description=f'```{response}```', colour=random_pastel_hex_colour)
    #     await interaction.send(embed=embed)

    @nextcord.slash_command(name='dice', description='Бросить кубики')
    async def dice(self, interaction: nextcord.Interaction,
                   count: int = nextcord.SlashOption(name='count', description='Количество кубиков', required=False)):
        count = 1 if count is None else count
        dice_numbs = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}
        embed = nextcord.Embed(title='Игровые кости 🎲', description='Выпало число...', colour=0x80a4d4)

        for i in range(count):
            rand = random.randint(1, 6)
            embed.add_field(name=f'``Бросок №{i + 1}``', value=f'```Выпало {dice_numbs[rand]} ({rand})!```')

        await interaction.send(embed=embed)
