from random import choice
import nextcord
from games.mafia.db import Player, Innocent, Mafia, Don, Doctor, Commissar, Bum, Slut, Morph, ROLES_DICT, SECONDARY_ROLES_LIMITS
from settings import MAFIA_BANNER_URL


class MafiaLobbyView(nextcord.ui.View):
    def __init__(self, status_interaction: nextcord.PartialInteractionMessage, author: nextcord.User | nextcord.Member):
        super().__init__()
        self.status_interaction: nextcord.PartialInteractionMessage = status_interaction
        self.lobby_lead = author
        self.secondary_roles_picker: MafiaSecondaryRolesView | None = None
        self.secondary_amount_picker: MafiaMemberAmountView | None = None
        self.invite_msg_id: int | None = None

    async def update(self):
        if self.secondary_roles_picker is None:
            self.secondary_roles_picker = MafiaSecondaryRolesView(self.status_interaction, self, self.lobby_lead)
        if self.secondary_amount_picker is None:
            self.secondary_amount_picker = MafiaMemberAmountView(self.status_interaction, self, self.lobby_lead)

        embed = nextcord.Embed(colour=0x2596BE, title='Настройки лобби')
        embed.add_field(name='```Дополнительные роли```',
                        value=f'```Бомж: {"✔️" if self.secondary_roles_picker.bum else "❌"}\n'
                              f'Ночная бабочка: {"✔️" if self.secondary_roles_picker.slut else "❌"}\n'
                              f'Морф: {"✔️" if self.secondary_roles_picker.morph else "❌"}```')
        embed.add_field(name='```Количество игроков```',
                        value=f'```{self.secondary_amount_picker.min} - {self.secondary_amount_picker.max}```')

        await self.status_interaction.edit(content=None, embed=embed)

    @nextcord.ui.button(label='Выбрать доп. роли', style=nextcord.ButtonStyle.gray, custom_id='select_secondary_roles')
    async def select_secondary_roles(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.status_interaction.edit(view=self.secondary_roles_picker)
        await self.secondary_roles_picker.update_message()
    
    @nextcord.ui.button(label='Выбрать кол-во игроков', style=nextcord.ButtonStyle.gray, custom_id='player_amount_picker')
    async def select_players_amount(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.status_interaction.edit(view=self.secondary_amount_picker)
        await self.secondary_amount_picker.update_message()

    @nextcord.ui.button(label='Описание ролей', style=nextcord.ButtonStyle.gray, custom_id='roles_desc')
    async def roles_desc(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        view = MafiaRolesDescView(self.status_interaction, self, self.lobby_lead)
        await self.status_interaction.edit(view=view)
        await view.update_message()

    @nextcord.ui.button(label='Описание режимов игры', style=nextcord.ButtonStyle.gray, custom_id='mode_desc')
    async def mode_desc(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        view = MafiaModeDesc(self.status_interaction, self, self.lobby_lead)
        await self.status_interaction.edit(view=view)
        await view.update()

    @nextcord.ui.button(label='Отослать приглашение в чат', style=nextcord.ButtonStyle.primary, custom_id='send_invite')
    async def send_invite(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        try:
            await interaction.channel.fetch_message(self.invite_msg_id)
        except (nextcord.NotFound, nextcord.HTTPException) as _:
            self.invite_msg_id = None

        if self.invite_msg_id is None:
            secondary_roles = [Bum if self.secondary_roles_picker.bum else None,
                               Slut if self.secondary_roles_picker.slut else None,
                               Morph if self.secondary_roles_picker.morph else None]
            secondary_roles = [i for i in secondary_roles if i is not None]
    
            status_interaction = await interaction.send('Creating invite...')
            view = MafiaGamePreLaunch(status_interaction, self.lobby_lead, self.secondary_amount_picker.min,
                                      self.secondary_amount_picker.max, secondary_roles)
            self.invite_msg_id = await status_interaction.fetch()
            self.invite_msg_id = self.invite_msg_id.id

            await status_interaction.edit(view=view)
            await view.update(add_view=True)
        else:
            await interaction.send('Приглашение уже отослано!', ephemeral=True)


class MafiaSecondaryRolesView(nextcord.ui.View):
    def __init__(self, status_interaction: nextcord.PartialInteractionMessage,
                 view_return_for: MafiaLobbyView, lobby_head: nextcord.User | nextcord.Member):
        super().__init__()
        self.view_return_for = view_return_for
        self.status_interaction: nextcord.PartialInteractionMessage = status_interaction
        self.lobby_head: nextcord.User | nextcord.Member = lobby_head
        self.bum: bool = False
        self.slut: bool = False
        self.morph: bool = False
    
    async def update_message(self):
        embed = nextcord.Embed(colour=0x2596BE, title='Дополнительные роли')
        embed.add_field(name='```Дополнительные роли```',
                        value=f'```Бомж (12-14+): {"✔️" if self.bum else "❌"}\n'
                              f'Ночная бабочка (15-17+): {"✔️" if self.slut else "❌"}\n'
                              f'Морф (18-20+): {"✔️" if self.morph else "❌"}\n```')
        await self.status_interaction.edit(embed=embed, view=self)

    @nextcord.ui.button(label='Назад', style=nextcord.ButtonStyle.green, custom_id='back')
    async def cancel(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.view_return_for.secondary_roles_picker = self
        
        await self.status_interaction.edit(view=self.view_return_for)
        await self.view_return_for.update()
    
    @nextcord.ui.button(label='Бомж', custom_id='bum_button')
    async def bum_button(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.bum = not self.bum
        await self.update_message()
    
    @nextcord.ui.button(label='Ночная бабочка', custom_id='slut_button')
    async def slut_button(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.slut = not self.slut
        await self.update_message()
    
    @nextcord.ui.button(label='Морф', custom_id='morph_button')
    async def morph_button(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.morph = not self.morph
        await self.update_message()
    
    @nextcord.ui.button(label='Назад', style=nextcord.ButtonStyle.primary, custom_id='back')
    async def cancel(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.view_return_for.secondary_roles_picker = self
        
        await self.status_interaction.edit(view=self.view_return_for)
        await self.view_return_for.update()


class MafiaMemberAmountView(nextcord.ui.View):
    def __init__(self, status_interaction: nextcord.PartialInteractionMessage,
                 view_return_for: MafiaLobbyView, lobby_head: nextcord.User | nextcord.Member):
        super().__init__()
        self.view_return_for = view_return_for
        self.status_interaction: nextcord.PartialInteractionMessage = status_interaction
        self.lobby_head: nextcord.User | nextcord.Member = lobby_head
        self.min: int = 6
        self.max: int = 6

    async def update_message(self):
        embed = nextcord.Embed(colour=0x2596BE, title='Игроки',
                               description=f'```Выбранное количество игроков: {self.min} - {self.max}```')
        await self.status_interaction.edit(embed=embed, view=self)
    
    @nextcord.ui.button(label='Назад', style=nextcord.ButtonStyle.green, custom_id='back')
    async def cancel(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.view_return_for.secondary_amount_picker = self
        
        await self.status_interaction.edit(view=self.view_return_for)
        await self.view_return_for.update()
    
    @nextcord.ui.button(label='6 - 6', style=nextcord.ButtonStyle.primary, custom_id='1')
    async def first(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.min, self.max = 6, 6
        await self.update_message()
    
    @nextcord.ui.button(label='7 - 7', style=nextcord.ButtonStyle.primary, custom_id='2')
    async def second(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.min, self.max = 7, 7
        await self.update_message()
    
    @nextcord.ui.button(label='8 - 11', style=nextcord.ButtonStyle.primary, custom_id='3')
    async def third(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.min, self.max = 8, 11
        await self.update_message()
    
    @nextcord.ui.button(label='12 - 14', style=nextcord.ButtonStyle.primary, custom_id='4')
    async def fourth(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.min, self.max = 12, 14
        await self.update_message()
    
    @nextcord.ui.button(label='15 - 17', style=nextcord.ButtonStyle.primary, custom_id='5')
    async def fifth(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.min, self.max = 15, 17
        await self.update_message()
    
    @nextcord.ui.button(label='18 - 20', style=nextcord.ButtonStyle.primary, custom_id='6')
    async def sixth(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.min, self.max = 18, 20
        await self.update_message()


class MafiaRolesDescView(nextcord.ui.View):
    def __init__(self, status_interaction: nextcord.PartialInteractionMessage,
                 view_return_for: MafiaLobbyView, lobby_head: nextcord.User | nextcord.Member):
        super().__init__()
        self.view_return_for = view_return_for
        self.status_interaction: nextcord.PartialInteractionMessage = status_interaction
        self.lobby_head = lobby_head

    async def update_message(self, update_embed: nextcord.Embed = nextcord.Embed(colour=0x2596BE, title='Описание роли', description='```Выберите роль```')):
        await self.status_interaction.edit(embed=update_embed, view=self)

    @nextcord.ui.button(label='Назад', style=nextcord.ButtonStyle.green, custom_id='back')
    async def cancel(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.view_return_for.secondary_roles_desc_view = self
        
        await self.status_interaction.edit(view=self.view_return_for)
        await self.view_return_for.update()
    
    @nextcord.ui.button(label='Мафия', style=nextcord.ButtonStyle.primary, custom_id='mafia_role_desc')
    async def mafia_role_desc(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.update_message(Mafia().desc_embed)

    @nextcord.ui.button(label='Дон', style=nextcord.ButtonStyle.primary, custom_id='don_role_desc')
    async def don_role_desc(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.update_message(Don().desc_embed)

    @nextcord.ui.button(label='Доктор', style=nextcord.ButtonStyle.primary, custom_id='doc_role_desc')
    async def doc_role_desc(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.update_message(Doctor().desc_embed)

    @nextcord.ui.button(label='Комиссар', style=nextcord.ButtonStyle.primary, custom_id='commissar_role_desc')
    async def commissar_role_desc(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.update_message(Commissar().desc_embed)

    @nextcord.ui.button(label='Бомж', style=nextcord.ButtonStyle.primary, custom_id='bum_role_desc')
    async def bum_role_desc(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.update_message(Bum().desc_embed)

    @nextcord.ui.button(label='Ночная бабочка', style=nextcord.ButtonStyle.primary, custom_id='slut_role_desc')
    async def slut_role_desc(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.update_message(Slut().desc_embed)

    @nextcord.ui.button(label='Морф', style=nextcord.ButtonStyle.primary, custom_id='morph_role_desc')
    async def morph_role_desc(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.update_message(Morph().desc_embed)


class MafiaModeDesc(nextcord.ui.View):
    def __init__(self, status_interaction: nextcord.PartialInteractionMessage,
                 view_return_for: MafiaLobbyView, lobby_head: nextcord.User | nextcord.Member):
        super().__init__()
        self.view_return_for = view_return_for
        self.status_interaction: nextcord.PartialInteractionMessage = status_interaction
        self.lobby_head = lobby_head
    
    async def update(self, update_embed: nextcord.Embed = nextcord.Embed(colour=0x2596BE, title='Описание режима',
                                                                         description='```Выберите режим```')):
        await self.status_interaction.edit(embed=update_embed, view=self)

    @nextcord.ui.button(label='Назад', style=nextcord.ButtonStyle.green, custom_id='back')
    async def cancel(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        self.view_return_for.secondary_roles_desc_view = self
        
        await self.status_interaction.edit(view=self.view_return_for)
        await self.view_return_for.update()
    
    @nextcord.ui.button(label='Ручной', style=nextcord.ButtonStyle.primary, custom_id='manual')
    async def manual_mode(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        embed = nextcord.Embed(colour=0x2596BE, title='Описание режима', description='```Бот выбирает роли, а организация игры полностью лежит на ведущем```')
        await self.update(embed)

    @nextcord.ui.button(label='Автоматический', style=nextcord.ButtonStyle.primary, custom_id='automatic')
    async def automatic_mode(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        embed = nextcord.Embed(colour=0x2596BE, title='Описание режима', description='```Бот выбирает роли и автоматически организовывает игру и все её события```')
        await self.update(embed)


class MafiaGamePreLaunch(nextcord.ui.View):
    def __init__(self, status_interaction: nextcord.PartialInteractionMessage, lobby_head: nextcord.User | nextcord.Member,
                 min_players: int, max_players: int, secondary_roles: list):
        super().__init__()
        self.status_interaction = status_interaction
        self.lobby_head = lobby_head
        self.min_players = min_players
        self.max_players = max_players
        self.players = []
        self.interactions_for_answer = []
        self.embed = nextcord.Embed(colour=nextcord.Colour.brand_green(), title='Приглашение в мафию!',
                                    description=f'{lobby_head.mention} приглашает вас в мафию!')
        self.embed.set_image(MAFIA_BANNER_URL)

        secondary_roles_ = [i for i in secondary_roles if f'{min_players}-{max_players}' in SECONDARY_ROLES_LIMITS[i]]
        roles: list = ROLES_DICT[f'{self.min_players}-{self.max_players}']

        for i in [Bum, Slut, Morph]:
            if i not in secondary_roles_ and i in roles:
                roles.remove(i)

        self.secondary_roles = secondary_roles_
        self.roles = roles

    async def update(self, add_view: bool):
        secondary_roles = ['Бомж' if self.secondary_roles.count(Bum) == 1 else '',
                           'Ночная бабочка' if self.secondary_roles.count(Slut) == 1 else '',
                           'Морф' if self.secondary_roles.count(Morph) == 1 else '']
        secondary_roles = ", ".join([i for i in secondary_roles if i != ''])
        secondary_text = '(заняты все места)\n' if len(self.players) == self.max_players else '\n'

        self.embed.clear_fields()
        self.embed.add_field(name='```Настройки игры```',
                             value=f'```Ограничения по игрокам: от {self.min_players} до {self.max_players}\n'
                                   f'Дополнительные роли: {"Отсутствуют" if secondary_roles == "" else secondary_roles}```')
        self.embed.add_field(name='```Игроки в лобби```',
                             value=f'Ведущий: {self.lobby_head.mention}\n\n{secondary_text}' + ' '.join([i.mention for i in self.players]))

        if add_view:
            await self.status_interaction.edit(content=None, embed=self.embed, view=self)
        else:
            await self.status_interaction.edit(content=None, embed=self.embed)

    async def check_for_lobby_author(self, new_interaction: nextcord.Interaction):
        return self.lobby_head == new_interaction.user

    @nextcord.ui.button(label='Запуск игры (ручной режим)', style=nextcord.ButtonStyle.primary, custom_id='start')
    async def start(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self.check_for_lobby_author(interaction):
            return

        if self.min_players <= len(self.players) <= self.max_players:
            await self.status_interaction.delete()

            prepared_players_list = []
            roles: list[classmethod] = self.roles
            players = self.players
            players.remove(self.lobby_head)

            for user, interaction_for_answer in zip(players, self.interactions_for_answer):
                if roles:
                    selected_role = choice(roles)
                    prepared_players_list.append(Player(user, selected_role(), interaction_for_answer))
                    roles.remove(selected_role)
                else:
                    prepared_players_list.append(Player(user, Innocent(), interaction_for_answer))

            player_list = '\n'.join([f'{player.nextcord_user.mention} - {str(player.role)}' for player in prepared_players_list])
            embed = nextcord.Embed(colour=nextcord.Colour.brand_green(), title='```Роли игроков```',
                                   description=player_list)
            await interaction.send(embed=embed, view=MafiaShowPlayersRoles(prepared_players_list), ephemeral=True)
        else:
            await interaction.send('Недостаточно игроков для начала игры!', ephemeral=True)

    @nextcord.ui.button(label='Присоединиться', style=nextcord.ButtonStyle.green, custom_id='join')
    async def join(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if len(self.players) != self.max_players \
                and interaction.user not in self.players \
                and interaction.user != self.lobby_head:
            self.players.append(interaction.user)
            self.interactions_for_answer.append(interaction)
    
            await self.update(add_view=True)


class MafiaShowPlayersRoles(nextcord.ui.View):
    def __init__(self, players: list[Player]):
        super().__init__()
        self.players = players

    @nextcord.ui.button(label='Показать всем игрокам роли', style=nextcord.ButtonStyle.green, custom_id='show_roles')
    async def show_roles(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        for player in self.players:
            await player.interaction_for_answer.send(f'{player.nextcord_user.mention} ```Твоя роль - {player.role}. {player.role.desc_embed.description.lstrip("`")}',
                                                     ephemeral=True)
