import nextcord.ext.commands


class VoteView(nextcord.ui.View):
    def __init__(self, bot: nextcord.ext.commands.Bot, parties: dict, status_message: nextcord.Message | None,
                 author: nextcord.User | nextcord.Member):
        super().__init__()
        self.bot = bot
        self.parties: dict = parties
        self.votes: dict = {}
        self.status_message = status_message
        self.author = author

    async def update(self):
        embed = self.status_message.embeds[0]
        embed.set_field_at(0, name='Проголосовали', value=f'```Проголосовали: {len(self.votes.keys())}```', inline=False)

        await self.status_message.edit(embed=embed, view=self)

    @nextcord.ui.button(label='Результаты', style=nextcord.ButtonStyle.green, custom_id='results')
    async def results(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != self.author:
            await interaction.send('Вы не являетесь организатором выборов!', ephemeral=True)
            return

        embed = nextcord.Embed(title='Parties 📊', colour=0x396ECC,
                               description='**Результаты выборов:**')

        parties = {}
        for user, party in self.votes.items():
            if party not in parties:
                parties |= {party: 1}
            else:
                parties[party] += 1
        for i in self.parties.keys():
            if i not in parties.keys():
                parties[i] = 0
        all_votes_cnt = sum(parties.values())

        best_party = ''
        best_party_votes = 0
        for party, votes_counts in parties.items():
            if votes_counts == max(list(parties.values())):
                best_party = party
                best_party_votes = votes_counts

            embed.add_field(name=f'`Партия "{party}"`', value=f'```Голоса: {votes_counts}\n'
                                                              f'Доля от всех голосов: {round(votes_counts / all_votes_cnt, 2) * 100}%```')

        embed.add_field(name='Итоги', value='```Победитель...\nЭто...```', inline=False)

        embed.add_field(name=f'`Партия "{best_party}"`', inline=False,
                        value=f'```Голоса: {best_party_votes}\n'
                              f'Доля от всех голосов: {round(best_party_votes / all_votes_cnt, 2) * 100}%```')

        await self.status_message.edit(embed=embed, view=None)
