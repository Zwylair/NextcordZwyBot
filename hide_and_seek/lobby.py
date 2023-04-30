from random import choice
import nextcord


class HideAndSeekView(nextcord.ui.View):
    def __init__(self, status_interaction: nextcord.PartialInteractionMessage, author: nextcord.User | nextcord.Member):
        super().__init__()
        self.status_interaction: nextcord.PartialInteractionMessage = status_interaction
        self.author = author
        self.seekers_pickup_view = HNSSeekersPickupView(status_interaction, self, author)
    
    async def update(self):
        embed = nextcord.Embed(colour=0x2596BE, title='Hide&Seek Настройки',
                               description=f'```Количество сикеров: {self.seekers_pickup_view.seekers_count}```')
        
        await self.status_interaction.edit(embed=embed, view=self)
    
    @nextcord.ui.button(label='Количество сикеров', style=nextcord.ButtonStyle.gray, custom_id='cnt_seekers')
    async def cnt_seekers(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        view = HNSSeekersPickupView(self.status_interaction, self, self.author)
        await view.update()

    @nextcord.ui.button(label='Отослать приглашение в чат', style=nextcord.ButtonStyle.primary, custom_id='send_invite')
    async def send_invite(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title='Wait please', description='Wait please...')
        status_interaction = await interaction.send(embed=embed)

        view = HNSLobby(status_interaction, self.author, self.seekers_pickup_view.seekers_count)
        await view.update()
        
        await self.status_interaction.delete()


class HNSSeekersPickupView(nextcord.ui.View):
    def __init__(self, status_interaction: nextcord.PartialInteractionMessage,
                 view_return_for: HideAndSeekView, author: nextcord.User | nextcord.Member):
        super().__init__()
        self.view_return_for = view_return_for
        self.status_interaction: nextcord.PartialInteractionMessage = status_interaction
        self.author = author
        self.seekers_count = 2
    
    async def update(self):
        embed = nextcord.Embed(colour=0x2596BE, title='Количество сикеров',
                               description=f'```Выбранное количество: {self.seekers_count}```')
        await self.status_interaction.edit(embed=embed, view=self)
    
    @nextcord.ui.button(label='Назад', style=nextcord.ButtonStyle.green, custom_id='back')
    async def cancel(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.view_return_for.seekers_pickup_view = self
        
        await self.status_interaction.edit(view=self.view_return_for)
        await self.view_return_for.update()
    
    @nextcord.ui.button(label='1', style=nextcord.ButtonStyle.primary, custom_id='one')
    async def one(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.seekers_count = 1
        await self.update()
    
    @nextcord.ui.button(label='2', style=nextcord.ButtonStyle.primary, custom_id='two')
    async def two(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.seekers_count = 2
        await self.update()
    
    @nextcord.ui.button(label='3', style=nextcord.ButtonStyle.primary, custom_id='three')
    async def three(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.seekers_count = 3
        await self.update()


class HNSLobby(nextcord.ui.View):
    def __init__(self, status_interaction: nextcord.PartialInteractionMessage, author: nextcord.User | nextcord.Member,
                 seekers_cnt: int):
        super().__init__()
        self.status_interaction = status_interaction
        self.author = author
        self.seekers_cnt = seekers_cnt
        self.players: [nextcord.User | nextcord.Member] = [self.author]
        self.were_previous_round = []
    
    async def update(self):
        embed = nextcord.Embed(colour=0x2596BE, title='Hide&Seek Lobby')
        embed.add_field(name='Количество сикеров', value=f'```Количество сикеров: {self.seekers_cnt}```')
        embed.add_field(name='Игроки', value=f'{", ".join([i.mention for i in self.players])}')
        
        await self.status_interaction.edit(embed=embed, view=self)

    async def check_for_lobby_author(self, new_interaction: nextcord.Interaction):
        return self.author == new_interaction.user

    @nextcord.ui.button(label='Присоединиться', style=nextcord.ButtonStyle.green, custom_id='join')
    async def join(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user not in self.players:
            self.players.append(interaction.user)
            await self.update()

    @nextcord.ui.button(label='Запуск игры', style=nextcord.ButtonStyle.primary, custom_id='start')
    async def start(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self.check_for_lobby_author(interaction):
            return
    
        if len(self.players) <= self.seekers_cnt:
            await interaction.send('Слишком мало людей участвует!', ephemeral=True)
            return

        to_seekers = [i for i in self.players if i not in self.were_previous_round]
        seekers = [choice(to_seekers)]
        for _ in range(self.seekers_cnt - 1):
            to_seekers.remove(seekers[-1])
            seekers.append(choice(to_seekers))

        self.were_previous_round = seekers

        embed = nextcord.Embed(title='Запуск игры', colour=nextcord.Colour.brand_green())
        embed.add_field(name='Сикеры', value=', '.join([i.mention for i in seekers]))
        embed.add_field(name='Прячущиеся', value=', '.join([i.mention for i in self.players if i not in seekers]))

        await self.status_interaction.edit(embed=embed, view=HNSBack(self.status_interaction, self, self.author))


class HNSBack(nextcord.ui.View):
    def __init__(self, status_interaction: nextcord.PartialInteractionMessage,
                 view_return_for: HNSLobby, author: nextcord.User | nextcord.Member):
        super().__init__()
        self.view_return_for = view_return_for
        self.status_interaction: nextcord.PartialInteractionMessage = status_interaction
        self.author = author

    @nextcord.ui.button(label='Назад', style=nextcord.ButtonStyle.green, custom_id='back')
    async def cancel(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.view_return_for.seekers_pickup_view = self
        
        await self.status_interaction.edit(view=self.view_return_for)
        await self.view_return_for.update()
