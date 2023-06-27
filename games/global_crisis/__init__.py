import random
import copy
import typing
import nextcord.ext.commands
import settings


class CancelView(nextcord.ui.View):
    def __init__(self, message: nextcord.Message):
        self.message = message
        super().__init__()

    @nextcord.ui.button(label='Отмена', style=nextcord.ButtonStyle.gray)
    async def cancel(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.message.delete()


class GlobalView(nextcord.ui.View):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        super().__init__()

        self.bot = bot
        self.users_in: list[nextcord.Member | None] | None = None
        self.countries_list = ['Армения', 'Германия', 'Казахстан', 'Нигер', 'США', 'Зимбабве', 'Швейцария', 'Япония', 'Украина', 'Ватикан', 'КНДР', 'Грузия']
        self.flags = [':flag_am:', ':flag_de:', ':flag_kz:', ':flag_ne:', ':flag_us:', ':flag_zw:', ':flag_ch:', ':flag_jp:', ':flag_ua:', ':flag_va:', ':flag_kp:', ':flag_ge:']

        # 8
        # self.countries_list = ['Армения', 'Германия', 'Казахстан', 'Нигер', 'США', 'Зимбабве', 'Швейцария', 'Украина']
        # self.flags = [':flag_am:', ':flag_de:', ':flag_kz:', ':flag_ne:', ':flag_us:', ':flag_zw:', ':flag_ch:', ':flag_ua:']

        self.enemies = {}
        self.allys = {}
        self.players = {}
        self.allow_to_regen_countries = True

    @staticmethod
    def check(author: nextcord.Member | nextcord.User, channel: typing.Any, message: nextcord.Message):
        return author.id == message.author.id and channel.id == message.channel.id

    @nextcord.ui.button(label='Add ids', style=nextcord.ButtonStyle.gray)
    async def add_ids(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):

        que = await interaction.send('Отправьте сообщение с айди через пробел', ephemeral=True)
        await que.edit(view=CancelView(que))
        msg_answer = await self.bot.wait_for('message', check=lambda x: self.check(interaction.user, interaction.channel, x))
        msg_answer: nextcord.Message = await msg_answer.channel.fetch_message(msg_answer.id)

        self.users_in = [interaction.guild.get_member(int(i)) for i in msg_answer.content.split(' ')]

        await que.delete()
        await msg_answer.delete()

    @nextcord.ui.button(label='Remove ids', style=nextcord.ButtonStyle.gray)
    async def remove_ids(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        que = await interaction.send('Отправьте сообщение с айди через пробел', ephemeral=True)
        await que.edit(view=CancelView(que))
        msg_answer = await self.bot.wait_for('message', check=lambda x: self.check(interaction.user, interaction.channel, x))
        msg_answer: nextcord.Message = await msg_answer.channel.fetch_message(msg_answer.id)

        content = msg_answer.content + ' ' if ' ' not in msg_answer.content else msg_answer.content
        for i in content.split(' '):
            if i != '':
                self.users_in.remove(interaction.guild.get_member(int(i)))

        await que.delete()
        await msg_answer.delete()

    @nextcord.ui.button(label='Show players + ids', style=nextcord.ButtonStyle.gray)
    async def show_ids(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title='ids', colour=nextcord.Colour.brand_green())
        embed.add_field(name='', value='\n'.join([f'{player.mention} ({self.flags[self.countries_list.index(country)]}) -> {player.id}' for player, country in self.players.items()]))

        await interaction.send(embed=embed, ephemeral=True)

    @nextcord.ui.button(label='Randomise countries', style=nextcord.ButtonStyle.gray)
    async def randomise(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.allow_to_regen_countries:
            countries_list = copy.deepcopy(self.countries_list)
            for i in self.users_in:
                country = random.choice(countries_list)
                self.players |= {i: country}
                countries_list.remove(country)

        embed = nextcord.Embed(title='Eta zalupa pizdec bagannaya, smotrite chtobi ne bilo povtorok na teh zhe liniyah', colour=nextcord.Colour.brand_green())
        players = [f'{k.mention}: {self.flags[self.countries_list.index(v)]}' for k, v in self.players.items()]
        embed.add_field(name='Players', value=' '.join(players), inline=False)

        # Generating enemies and allys
        enemy_target = copy.deepcopy(self.countries_list)
        enemies = {}
        for i in self.countries_list:
            enemy = ''
            for _ in range(999):
                enemy = random.choice(enemy_target)
                if enemy != i:
                    break
            enemies |= {i: enemy}
            enemy_target.remove(enemy)

        # allys
        ally_target = copy.deepcopy(self.countries_list)
        allys = {}
        for i in self.countries_list:
            ally = ''
            for _ in range(999):
                ally = random.choice(ally_target)
                if i != ally and enemies[i] != ally:
                    break

            allys |= {i: ally}
            ally_target.remove(ally)

        self.enemies = enemies
        self.allys = allys

        allys_emoji = {}
        for country1, country2 in self.allys.items():
            allys_emoji |= {
                self.flags[self.countries_list.index(country1)]: self.flags[self.countries_list.index(country2)]}
        enemies_emoji = {}
        for country1, country2 in self.enemies.items():
            enemies_emoji |= {self.flags[self.countries_list.index(country1)]: self.flags[self.countries_list.index(country2)]}
        
        ally_list = [f'{k} -> {v}' for k, v in allys_emoji.items()]
        enemy_list = [f'{k} -> {v}' for k, v in enemies_emoji.items()]
        embed.add_field(name='Enemies', value='\n'.join(enemy_list))
        embed.add_field(name='.', value='\n'*12)
        embed.add_field(name='Allys', value='\n'.join(ally_list))

        await interaction.send(embed=embed, ephemeral=True)

    @nextcord.ui.button(label='Allow/disallow countries regen', style=nextcord.ButtonStyle.gray)
    async def countries_regen(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.allow_to_regen_countries = not self.allow_to_regen_countries
    
        await interaction.send(f'self.allow_to_regen_countries is now {self.allow_to_regen_countries}', ephemeral=True)

    @nextcord.ui.button(label='Set countries', style=nextcord.ButtonStyle.gray)
    async def set_countries(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        que = await interaction.send('Отправьте сообщение с template as "<player-ds-id>=<country-id-in-list> <player-ds-id>=<country-id-in-list>..."', ephemeral=True)
        await que.edit(view=CancelView(que))
        msg_answer = await self.bot.wait_for('message', check=lambda x: self.check(interaction.user, interaction.channel, x))
        msg_answer: nextcord.Message = await msg_answer.channel.fetch_message(msg_answer.id)
    
        content = msg_answer.content + ' ' if ' ' not in msg_answer.content else msg_answer.content
        self.players = {}
        for line in content.split(' '):
            if line:
                raw_player_info = line.split('=')
                raw_player, raw_player_country_id = raw_player_info
                player = interaction.guild.get_member(int(raw_player))
                country = self.countries_list[int(raw_player_country_id)]
                
                self.players |= {player: country}

        await que.delete()
        await msg_answer.delete()

        embed = nextcord.Embed(title='Ya chepush', colour=nextcord.Colour.brand_green())
        players = [f'{k.mention}: {self.flags[self.countries_list.index(v)]}' for k, v in self.players.items()]
        embed.add_field(name='Players', value=' '.join(players), inline=False)

        await interaction.send('Players now:', embed=embed, ephemeral=True)

    @nextcord.ui.button(label='Send cards', style=nextcord.ButtonStyle.gray)
    async def send_cards(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        players_list: list[nextcord.Member] = list(self.players.keys())

        for player_member in players_list:
            country_name = self.players[player_member]
            country_id = self.countries_list.index(country_name)
            player_number = players_list.index(player_member) + 1

            enemy_to_me_id = self.countries_list.index(self.enemies[country_name])
            ally_to_me_id = self.countries_list.index(self.allys[country_name])

            embed = nextcord.Embed(title='Карточка :black_joker:', colour=0x3aa3e5, description=f'Ты - игрок №{player_number}')
            embed.add_field(name='Твоя страна', value=f'`Твоя страна: {country_name} `{self.flags[country_id]}')
            embed.add_field(name='Твой враг', value=f'`Твой враг: {self.countries_list[enemy_to_me_id]} `{self.flags[enemy_to_me_id]}')
            embed.add_field(name='Твой союзник', value=f'`Твой вынужденный союзник: {self.countries_list[ally_to_me_id]} `{self.flags[ally_to_me_id]}')

            failed_to_send = []
            try:
                await player_member.send(embed=embed)
            except nextcord.Forbidden:
                failed_to_send.append(player_member)
            
            if failed_to_send:
                await interaction.send(f'У этих парней закрыта личка... {", ".join([f"{i.mention}" for i in failed_to_send])}', ephemeral=True)


class GlobalCrisis(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot
        # self.author: nextcord.User | nextcord.Member | None = None
    
    # def check(self, message: nextcord.Message):
    #     return self.author.id == message.author.id
    
    # @nextcord.slash_command(name='meme', description='meme')
    # async def meme(self, _: nextcord.Interaction):
    #     pass

    @nextcord.slash_command(name='global_crisis_dev', description='Global Crisis DEV')
    async def global_crisis_dev(self, interaction: nextcord.Interaction):
        if interaction.user.id != settings.OWNER_ID:
            msg = await interaction.send('Declined', ephemeral=True)
            await msg.delete()

            return

        await interaction.send('Global crisis', view=GlobalView(self.bot), ephemeral=True)


def setup(bot):
    bot.add_cog(GlobalCrisis(bot))
