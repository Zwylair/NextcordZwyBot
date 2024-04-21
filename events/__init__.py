from typing import Literal
import nextcord.ext.commands
from settings import *
from events.funcs import *
from events.create_embed_view import CreateEmbedView
from events.remove_template_select import RemoveTemplateSelect
from events.template_select import TemplateSelect
import db


class EventsCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='events', description='events')
    async def events(self, _: nextcord.Interaction):
        pass

    @events.subcommand(name='create', description='Создать событие')
    async def create(
            self, interaction: nextcord.Interaction,
            day: Literal[tuple(DATETIME_WEEKDAY_DICT.values())] = nextcord.SlashOption(
                name='day', required=True,
                description='День проведения ивента'
            ),
            time: str = nextcord.SlashOption(
                name='time', required=True,
                description='Время проведения ивента (например 21:00)'
            ),
            out_channel: nextcord.TextChannel = nextcord.SlashOption(
                name='chat', required=True,
                description='Чат назначения'
            )
    ):

        input_day_num = {v: k for k, v in DATETIME_WEEKDAY_DICT.items()}[day]
        nowadays_index = datetime.date.today().weekday()
        hour, minute = [int(i) for i in time.split(':')]

        embed = nextcord.Embed(title='Title', description='Desc', colour=0x9a72ba)
        embed.set_image(VERIFY_BANNER_URL)
        embed.timestamp = get_event_datetime(nowadays_index, input_day_num, hour, minute)

        msg = await interaction.send(embed=embed, ephemeral=True)
        view = CreateEmbedView(self.bot, interaction, msg, embed, out_channel)
        await msg.edit(view=view)

    @events.subcommand(name='use_template', description='Использовать шаблон')
    async def use_template(
            self, interaction: nextcord.Interaction,
            day: Literal[tuple(DATETIME_WEEKDAY_DICT.values())] = nextcord.SlashOption(
                name='day', required=True,
                description='День проведения ивента'
            ),
            time: str = nextcord.SlashOption(
                name='time', required=True,
                description='Время проведения ивента (например 21:00)'
            ),
            out_channel: nextcord.TextChannel = nextcord.SlashOption(
                name='chat', required=True,
                description='Чат назначения'
            )
    ):
        input_day_num = {v: k for k, v in DATETIME_WEEKDAY_DICT.items()}[day]
        nowadays_index = datetime.date.today().weekday()
        hour, minute = [int(i) for i in time.split(':')]

        cur = db.get_cursor()
        cur.execute("SELECT * FROM event_templates WHERE server_id = ?", (interaction.guild_id,))
        rows = cur.fetchall()
        cur.close()

        templates = {'-': ''}
        options = []

        for i in rows:
            _, template_name, pickled_embed = i
            templates[template_name] = pickled_embed
            options.append(nextcord.SelectOption(label=template_name))

        msg = await interaction.send('Выберите шаблон, который вы хотите использовать:', ephemeral=True)

        view = nextcord.ui.View()
        view.add_item(
            TemplateSelect(
                options_dict=templates, options=options,
                event_datetime=get_event_datetime(nowadays_index, input_day_num, hour, minute),
                msg=msg, bot=self.bot, out_channel=out_channel
            )
        )
        await msg.edit(view=view)

    @events.subcommand(name='delete_template', description='Удалить шаблон')
    async def delete_template(self, interaction: nextcord.Interaction):
        cur = db.get_cursor()
        cur.execute("SELECT * FROM event_templates WHERE server_id = ?", (interaction.guild_id,))
        rows = cur.fetchall()
        cur.close()

        templates = {'-': ''}
        for i in rows:
            _, template_name, pickled_embed = i
            templates[template_name] = pickled_embed

        msg = await interaction.send('Выберите шаблон, который вы хотите удалить:', ephemeral=True)
        view = nextcord.ui.View()
        view.add_item(RemoveTemplateSelect(options_dict=templates, bot=self.bot, msg=msg))

        await msg.edit(view=view)


def setup(bot):
    bot.add_cog(EventsCog(bot))
