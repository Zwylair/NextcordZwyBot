from dataclasses import dataclass
import nextcord.ext.commands
from settings import *
import db


@dataclass
class DeleteOptions:
    NOBODY_IN_VOICE = 1
    LOCALIZATION = {
        NOBODY_IN_VOICE: 'Никого в гс',
    }


@dataclass
class ActionWithUsers:
    ADD = 1
    REMOVE = 2


class SetupPrivateVoiceView(nextcord.ui.View):
    def __init__(
            self, status_message: nextcord.PartialInteractionMessage,
            author: nextcord.Member,
            bot: nextcord.ext.commands.Bot
    ):
        super().__init__()

        self.bot = bot
        self.author = author
        self.status_message = status_message
        self.vc_name = ''
        self.people_limit: int | None = None
        self.delete_option = DeleteOptions.NOBODY_IN_VOICE
        self.allowed_members = [author]

        self.set_vc_name_to_default()

    def set_vc_name_to_default(self):
        # user.nick is server name of user. using default name if not set
        author_name = self.author.global_name if self.author.nick is None else self.author.nick
        self.vc_name = f'{author_name}\'s channel'

    async def update_embed(self):
        members_str = ' '.join([i.mention for i in self.allowed_members])
        people_limit_str = 'Нет' if self.people_limit is None else self.people_limit
        delete_str = DeleteOptions.LOCALIZATION[self.delete_option]
        vc_name_str = self.vc_name

        embed = nextcord.Embed(title=vc_name_str, color=0xFFFFFF)
        embed.add_field(name='Участники', value=members_str, inline=False)
        embed.add_field(name='Лимит участников', value=people_limit_str)
        embed.add_field(name='Удаление при', value=delete_str)

        await self.status_message.edit(content='', embed=embed)

    @nextcord.ui.button(emoji=PRIVATE_VC.get('create'), style=nextcord.ButtonStyle.primary)
    async def create(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.voice is None:
            await interaction.send('Перейдите в любой гс для продолжения!', ephemeral=True)
            return

        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute(
            'SELECT vc_category FROM private_vc_config WHERE server_id=?',
            (interaction.guild_id,)
        )

        vc_category_id = cur.fetchone()
        if vc_category_id is not None:
            vc_category_id = vc_category_id[0]

        vc_category: nextcord.CategoryChannel | None = interaction.guild.get_channel(vc_category_id)
        vc_category_permissions = nextcord.PermissionOverwrite(speak=False, stream=False,
                                                               start_embedded_activities=False)
        vc_permissions = {interaction.guild.default_role: nextcord.PermissionOverwrite(connect=False)}
        vc_permissions |= {member: nextcord.PermissionOverwrite(connect=True) for member in self.allowed_members}

        if vc_category is None:
            vc_category = await interaction.guild.create_category('PRIVATE VOICE',
                                                                  reason='saved voice category was deleted')

            cur.execute(
                'INSERT INTO private_vc_config VALUES (?, ?)',
                (interaction.guild_id, vc_category.id)
            )

        await vc_category.set_permissions(interaction.guild.default_role, overwrite=vc_category_permissions)
        private_channel = await interaction.guild.create_voice_channel(
            name=self.vc_name,
            category=vc_category,
            user_limit=self.people_limit,
            overwrites=vc_permissions
        )

        cur.execute(
            'INSERT INTO private_vc VALUES (?, ?)',
            (interaction.guild_id, private_channel.id)
        )
        conn.commit()
        cur.close()
        conn.close()

        await self.author.move_to(private_channel)
        await self.status_message.delete()
        await interaction.send('Готово!', ephemeral=True)

    @nextcord.ui.button(emoji=PRIVATE_VC.get('change_name'))
    async def change_name(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        modal = ChangeNameModal(self)
        await interaction.response.send_modal(modal)

    @nextcord.ui.button(emoji=PRIVATE_VC.get('add_users'))
    async def add_members(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        view = nextcord.ui.View()
        msg = await interaction.send('Выберите людей, которым будет разрешен доступ к каналу', ephemeral=True)
        view.add_item(UserSelectItem(self, msg, ActionWithUsers.ADD))
        await msg.edit(view=view)

    @nextcord.ui.button(emoji=PRIVATE_VC.get('remove_users'))
    async def remove_members(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        view = nextcord.ui.View()
        msg = await interaction.send('Выберите людей, которым будет убран доступ к каналу', ephemeral=True)
        view.add_item(UserSelectItem(self, msg, ActionWithUsers.REMOVE))
        await msg.edit(view=view)

    @nextcord.ui.button(emoji=PRIVATE_VC.get('change_limit'))
    async def change_people_limit(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        modal = PeopleLimitModal(self)
        await interaction.response.send_modal(modal)


class UserSelectItem(nextcord.ui.UserSelect):
    def __init__(
            self, change_view: SetupPrivateVoiceView,
            status_message: nextcord.PartialInteractionMessage,
            action: int
    ):
        super().__init__(max_values=25)
        self.action = action
        self.change_view = change_view
        self.status_message = status_message

    async def callback(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title='Добавление участников: результаты', color=0xFFFFFF)
        add_members = []
        remove_members = []
        allowed_members_ids = [i.id for i in self.change_view.allowed_members]

        if self.action == ActionWithUsers.ADD:
            for member in self.values:
                if member.id in allowed_members_ids:
                    embed.add_field(name=member.display_name, value='✅ (уже добавлен)')
                    continue

                embed.add_field(name=member.display_name, value='✅')
                add_members.append(member)

            self.change_view.allowed_members += add_members
        elif self.action == ActionWithUsers.REMOVE:
            for member in self.values:
                if member.id not in allowed_members_ids:
                    embed.add_field(name=member.display_name, value='✅ (не в списке)')
                    continue

                if member.id == self.change_view.author.id:
                    embed.add_field(name=member.display_name, value='❌ (нельзя убрать себя)')
                    continue

                embed.add_field(name=member.display_name, value='✅')
                remove_members.append(member)

            for i in remove_members:
                self.change_view.allowed_members.pop(allowed_members_ids.index(i.id))
                allowed_members_ids.pop(allowed_members_ids.index(i.id))

        await self.status_message.edit(content=None, embed=embed, view=None)
        await self.change_view.update_embed()


class PeopleLimitModal(nextcord.ui.Modal):
    def __init__(self, view: SetupPrivateVoiceView):
        self.view = view

        super().__init__(
            'Лимит участников',
            timeout=5 * 60,
        )

        self.people_limit = nextcord.ui.TextInput(
            label='Лимит участников (0 для неограниченного)',
            min_length=0,
            max_length=2,
            required=True
        )
        self.add_item(self.people_limit)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.people_limit.value

        if not value.isdigit():
            await interaction.send('Лимит должен содержать только цифры!', ephemeral=True)
            return
        value = int(value)

        self.view.people_limit = None if value == 0 else value
        await self.view.update_embed()


class ChangeNameModal(nextcord.ui.Modal):
    def __init__(self, view: SetupPrivateVoiceView):
        self.view = view

        super().__init__(
            'Название канала',
            timeout=5 * 60,
        )

        self.vc_name = nextcord.ui.TextInput(
            label='Название (пустое = по умолчанию)',
            min_length=0,
            max_length=99,
            required=False
        )
        self.add_item(self.vc_name)

    async def callback(self, interaction: nextcord.Interaction):
        value = self.vc_name.value

        if not value:
            self.view.set_vc_name_to_default()
        else:
            self.view.vc_name = value

        await self.view.update_embed()
