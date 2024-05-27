import json
from dataclasses import dataclass
import nextcord.ext.commands
from temp_voice.setup_temp_voice import SetupPrivateVoiceView
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


class ModifyPrivateVoiceView(nextcord.ui.View):
    def __init__(
            self, vc_setup_view: SetupPrivateVoiceView,
            voice_channel: nextcord.VoiceChannel,
            interaction: nextcord.Interaction
    ):
        super().__init__(timeout=60 * 60)

        self.bot = vc_setup_view.bot
        self.voice_channel = voice_channel
        self.interaction = interaction
        self.author = vc_setup_view.author
        self.status_message = vc_setup_view.status_message
        self.vc_name = vc_setup_view.vc_name
        self.people_limit = vc_setup_view.people_limit
        self.delete_option = vc_setup_view.delete_option
        self.allowed_members = [self.author]

    async def set_vc_name_to_default(self, user: nextcord.Member):
        # user.nick is server name of user. using default name if not set
        author_name = self.author.global_name if self.author.nick is None else self.author.nick
        await self.update_vc(user, vc_name=f'{author_name}\'s channel')

    def check_for_vc_author(self, user: nextcord.Member | nextcord.User):
        return user.id == self.author.id

    async def update_vc(
            self, user: nextcord.Member,
            vc_name: str = None,
            people_limit: int = None,
            delete_option: str = None,
            allowed_members: dict[nextcord.Role | nextcord.Member, nextcord.PermissionOverwrite] = None
    ):
        if not self.check_for_vc_author(user):
            await self.interaction.send('Вы не создатель приватного канала!', ephemeral=True)
            return

        author = self.author.guild.get_member(self.author.id)
        if author.voice is None:
            await self.interaction.send('Вы не находитесь в приватном канале!', ephemeral=True)
            return

        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute(
            'SELECT vc_channel_id FROM private_vc WHERE server_id=? AND vc_channel_id=?',
            (author.guild.id, author.voice.channel.id)
        )
        fetch = cur.fetchone()

        if fetch is None:
            await self.interaction.send('Вы находитесь не в приватном канале!', ephemeral=True)
            return

        if vc_name is not None:
            self.vc_name = vc_name
            await self.voice_channel.edit(name=vc_name)

        if people_limit is not None:
            cur.execute(
                'UPDATE private_vc SET people_limit=? WHERE server_id=? AND vc_channel_id=?',
                (people_limit, self.author.guild.id, self.voice_channel.id)
            )
            self.people_limit = None if people_limit == 0 else people_limit
            await self.voice_channel.edit(user_limit=people_limit)

        if delete_option is not None:
            cur.execute(
                'UPDATE private_vc SET delete_option=? WHERE server_id=? AND vc_channel_id=?',
                (delete_option, self.author.guild.id, self.voice_channel.id)
            )
            self.delete_option = delete_option

        if allowed_members is not None:
            allowed_members_ids = [i.id for i in self.allowed_members]
            allowed_members_ids = json.dumps(allowed_members_ids)

            cur.execute(
                'UPDATE private_vc SET allowed_members=? WHERE server_id=? AND vc_channel_id=?',
                (allowed_members_ids, self.author.guild.id, self.voice_channel.id)
            )
            await self.voice_channel.edit(overwrites=allowed_members)

        conn.commit()
        cur.close()
        conn.close()

        await self.update_embed()

    async def update_embed(self):
        members_str = ' '.join([i.mention for i in self.allowed_members])
        people_limit_str = 'Нет' if self.people_limit is None else self.people_limit
        delete_str = DeleteOptions.LOCALIZATION[self.delete_option]
        vc_name_str = self.vc_name

        embed = nextcord.Embed(title=vc_name_str, color=0xFFFFFF)
        embed.add_field(name='Участники', value=members_str, inline=False)
        embed.add_field(name='Лимит участников', value=people_limit_str)
        embed.add_field(name='Удаление при', value=delete_str)

        await self.status_message.edit(content=None, embed=embed)

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
            self, change_view: ModifyPrivateVoiceView,
            status_message: nextcord.PartialInteractionMessage,
            action: int
    ):
        super().__init__(max_values=25)
        self.action = action
        self.change_view = change_view
        self.status_message = status_message

    async def callback(self, interaction: nextcord.Interaction):
        add_members = []
        remove_members = []
        new_permissions = {}
        allowed_members_ids = [i.id for i in self.change_view.allowed_members]
        embed = nextcord.Embed()

        if self.action == ActionWithUsers.ADD:
            embed = nextcord.Embed(title='Добавление участников: результаты', color=0xFFFFFF)

            for member in self.values:
                if member.id in allowed_members_ids:
                    embed.add_field(name=member.display_name, value='✅ (уже добавлен)')
                    continue

                embed.add_field(name=member.display_name, value='✅')
                add_members.append(member)

            new_permissions = {member: nextcord.PermissionOverwrite(connect=True) for member in add_members}
            self.change_view.allowed_members += add_members
        elif self.action == ActionWithUsers.REMOVE:
            embed = nextcord.Embed(title='Удаление участников: результаты', color=0xFFFFFF)

            for member in self.values:
                if member.id not in allowed_members_ids:
                    embed.add_field(name=member.display_name, value='✅ (не в списке)')
                    continue

                if member.id == self.change_view.author.id:
                    embed.add_field(name=member.display_name, value='❌ (нельзя убрать себя)')
                    continue

                embed.add_field(name=member.display_name, value='✅')
                remove_members.append(member)

            new_permissions = {member: nextcord.PermissionOverwrite(connect=False) for member in remove_members}
            for i in remove_members:
                self.change_view.allowed_members.pop(allowed_members_ids.index(i.id))
                allowed_members_ids.pop(allowed_members_ids.index(i.id))

        await self.status_message.edit(content=None, embed=embed, view=None)
        await self.change_view.update_vc(interaction.user, allowed_members=new_permissions)


class PeopleLimitModal(nextcord.ui.Modal):
    def __init__(self, view: ModifyPrivateVoiceView):
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

        await self.view.update_vc(interaction.user, people_limit=value)


class ChangeNameModal(nextcord.ui.Modal):
    def __init__(self, view: ModifyPrivateVoiceView):
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
            await self.view.set_vc_name_to_default(interaction.user)
        else:
            await self.view.update_vc(interaction.user, vc_name=value)
