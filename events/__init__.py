import pickle
import sqlite3
import urllib.parse
import datetime
import typing
import nextcord.ext.commands
from verifier.errors import ErrorOrganizer
import settings


def check_verifier_args(bot: nextcord.ext.commands.Bot, chat: nextcord.TextChannel | None = None,
                        hex_colour: str | None = None,
                        banner_url: str | None = None) -> ErrorOrganizer:
    errors_organizer = ErrorOrganizer()
    
    if chat is not None:
        bot_as_member = [i for i in bot.get_all_members() if i.id == bot.user.id][0]
        bot_perms = chat.permissions_for(bot_as_member)
        
        errors_organizer.chat_state = False if bot_perms.manage_messages else True
    
    if hex_colour is not None:
        try:
            int(hex_colour.lstrip("#"), 16)
            errors_organizer.colour_state = False
        except BaseException:
            errors_organizer.colour_state = True
    
    if banner_url is not None:
        result = urllib.parse.urlparse(banner_url)
        errors_organizer.banner_state = not all([result.scheme, result.netloc])
    
    return errors_organizer


class CreateEmbedView(nextcord.ui.View):
    def __init__(self, bot: nextcord.ext.commands.Bot, base_interaction: nextcord.Interaction,
                 embed_message: nextcord.PartialInteractionMessage, out_embed: nextcord.Embed,
                 out_chat: nextcord.TextChannel):
        super().__init__()
    
        self.bot = bot
        self.base_interaction = base_interaction
        self.embed_message = embed_message
        self.out_embed = out_embed
        self.out_chat = out_chat
        self.give_role: nextcord.Role | None = None
    
    def check(self, message: nextcord.Message):
        return self.base_interaction.user.id == message.author.id
    
    async def check_for_command_sender(self, interaction: nextcord.Interaction):
        return self.base_interaction.user.id == interaction.user.id
    
    async def update_embed(self):
        await self.embed_message.edit(content='Предпоказ сообщения', embed=self.out_embed, view=self)
    
    async def update_out_embed(self, title: str | None = None, desc: str | None = None, colour: int | None = None,
                               banner_url: str | None = None, thumb_url: str | None = None):
        title = self.out_embed.title if title is None else title
        desc = self.out_embed.description if desc is None else desc
        colour = self.out_embed.colour if colour is None else colour
        banner_url = self.out_embed.image.url if banner_url is None else banner_url
        thumb_url = self.out_embed.thumbnail.url if thumb_url is None else thumb_url
        timestamp = self.out_embed.timestamp
        
        embed = nextcord.Embed(title=title, description=desc, colour=colour, timestamp=timestamp)
        embed.set_thumbnail(thumb_url)
        embed.set_image(banner_url)
        self.out_embed = embed

    @nextcord.ui.button(label='Сохранить как шаблон', style=nextcord.ButtonStyle.green)
    async def save_as_template(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self.check_for_command_sender(interaction):
            return

        que = await interaction.send('Отправьте название шаблона в чат (не больше 256 символов)', ephemeral=True)
    
        name_answer = await self.bot.wait_for('message', check=self.check)
        name_answer: nextcord.Message = await name_answer.channel.fetch_message(name_answer.id)
    
        if len(name_answer.content) > 256:
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Название превышает 256 символов!')
        
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return
    
        dumped = pickle.dumps(self.out_embed)
        
        sql = sqlite3.connect(settings.SQL_DB_PATH)
        sql.execute(f'''INSERT INTO event_templates (server_id, template_name, embed_bytes) VALUES ("{interaction.guild_id}", "{name_answer}", "{dumped}")''')

        await interaction.send('Сохранено', ephemeral=True)
        await name_answer.delete()
        await que.delete()

    @nextcord.ui.button(label='Изменить название')
    async def edit_embed_title(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self.check_for_command_sender(interaction):
            return
        
        que = await interaction.send('Отправьте заголовок в чат (не больше 256 символов)', ephemeral=True)
        
        title_answer = await self.bot.wait_for('message', check=self.check)
        title_answer: nextcord.Message = await title_answer.channel.fetch_message(title_answer.id)
        
        if len(title_answer.content) > 256:
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Заголовок превышает 256 символов!')
            
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return
        
        await self.update_out_embed(title=title_answer.content)
        
        await title_answer.delete()
        await que.delete()
        await self.update_embed()
    
    @nextcord.ui.button(label='Изменить описание')
    async def edit_embed_description(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self.check_for_command_sender(interaction):
            return
        
        que = await interaction.send('Отправьте описание в чат (не больше 2048 символов)', ephemeral=True)
        
        description_answer = await self.bot.wait_for('message', check=self.check)
        description_answer: nextcord.Message = await description_answer.channel.fetch_message(description_answer.id)
        
        if len(description_answer.content) > 2048:
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Описание превышает 2048 символов!')
            
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return
        
        await self.update_out_embed(desc=description_answer.content)
        
        await description_answer.delete()
        await que.delete()
        await self.update_embed()

    @nextcord.ui.button(label='Изменить картинку')
    async def edit_embed_image(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self.check_for_command_sender(interaction):
            return
        
        que = await interaction.send('Отправьте ссылку на баннер в чат (gif/jpg/png)', ephemeral=True)
        banner_answer = await self.bot.wait_for('message', check=self.check)
        banner_answer: nextcord.Message = await banner_answer.channel.fetch_message(banner_answer.id)
        
        if check_verifier_args(self.bot, banner_url=banner_answer.content).is_one_an_error():
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Неверная ссылка на баннер!')
            
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return
        
        await self.update_out_embed(banner_url=banner_answer.content)
        
        await que.delete()
        await banner_answer.delete()
        await self.update_embed()
    
    @nextcord.ui.button(label='Изменить цвет')
    async def edit_embed_color(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self.check_for_command_sender(interaction):
            return
        
        que = await interaction.send('Отправьте цвет в формате hex, пример: `#f73a02`', ephemeral=True)
        color_answer = await self.bot.wait_for('message', check=self.check)
        color_answer: nextcord.Message = await color_answer.channel.fetch_message(color_answer.id)
        
        hex_col = color_answer.content.lstrip('#')
        if check_verifier_args(self.bot, hex_colour=hex_col).is_one_an_error():
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Неверно указан цвет hex!')
            
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return
        
        await self.update_out_embed(colour=int(hex_col, 16))
        
        await que.delete()
        await color_answer.delete()
        await self.update_embed()

    @nextcord.ui.button(label='Изменить картинку предпоказа')
    async def edit_thumbnail(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self.check_for_command_sender(interaction):
            return
    
        que = await interaction.send('Отправьте ссылку на баннер в чат (jpg/png)', ephemeral=True)
        banner_answer = await self.bot.wait_for('message', check=self.check)
        banner_answer: nextcord.Message = await banner_answer.channel.fetch_message(banner_answer.id)
    
        if check_verifier_args(self.bot, banner_url=banner_answer.content).is_one_an_error():
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Неверная ссылка на баннер!')
        
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return

        await self.update_out_embed(thumb_url=banner_answer.content)
    
        await que.delete()
        await banner_answer.delete()
        await self.update_embed()

    @nextcord.ui.button(label='📨', style=nextcord.ButtonStyle.green)
    async def send_button_callback(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.out_chat.send(embed=self.out_embed)
    
        await interaction.send('Сообщение отправлено!', ephemeral=True)
        await self.embed_message.delete()


class EventsCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='events', description='events')
    async def events(self, _: nextcord.Interaction):
        pass

    @events.subcommand(name='create', description='Создать событие')
    async def create(self, interaction: nextcord.Interaction,
                     day: typing.Literal['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] = nextcord.SlashOption(name='day', description='День проведения ивента', required=True),
                     time: str = nextcord.SlashOption(name='time', description='Время проведения ивента (например 21:00)', required=True),
                     out_channel: nextcord.TextChannel = nextcord.SlashOption(name='chat', description='Чат назначения', required=True)):

        input_day_num = {v: k for k, v in settings.DATETIME_WEEKDAY_DICT.items()}[day]
        today_num = datetime.date.today().weekday()
    
        # Ебать сложные махинации с датой я сделал нахуй, я рот ебал нахуй этой хуйни блядота ёбаная
        interval = input_day_num - today_num if today_num < input_day_num else 7 - today_num + input_day_num
        interval = 0 if interval == 7 else interval
        hour, minute = [int(i) for i in time.split(':')]
        date_now = datetime.datetime.utcnow()
        date_now = date_now.replace(hour=hour, minute=minute)
        # в последнее воскресенье марта в 3:00 на 1 час вперед
        # в последнее воскресенье октября в 4:00 на 1 час назад.
        # date_now -= datetime.timedelta(hours=2)  # Hot-fix for host
        timestamp = date_now + datetime.timedelta(days=interval)

        embed = nextcord.Embed(title='Title', description='Desc', colour=0x9a72ba)
        embed.set_image(settings.VERIFY_BANNER_URL)
        embed.timestamp = timestamp

        msg = await interaction.send(embed=embed, ephemeral=True)
        view = CreateEmbedView(self.bot, interaction, msg, embed, out_channel)

        await msg.edit(view=view)

    @events.subcommand(name='use_template', description='Использовать шаблон')
    async def use_template(self, interaction: nextcord.Interaction,
                           day: typing.Literal['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] = nextcord.SlashOption(name='day', description='День проведения ивента', required=True),
                           time: str = nextcord.SlashOption(name='time', description='Время проведения ивента (например 21:00)', required=True),
                           out_channel: nextcord.TextChannel = nextcord.SlashOption(name='chat', description='Чат назначения', required=True)):
        class SelectItem(nextcord.ui.Select):
            def __init__(self, saved_templates: list[dict], options: list[nextcord.SelectOption]):
                super().__init__(options=options)
                self.saved_templates = saved_templates
            
            async def callback(self, interaction_: nextcord.Interaction):
                await interaction_.send(f'{self.values[0]}')

        sql = sqlite3.connect(settings.SQL_DB_PATH)
        req = sql.execute(f'SELECT * FROM event_templates WHERE server_id = {interaction.guild_id}').fetchall()
        templates = []
        options_ = []
        for i in req:
            server_id, template_name, pickled_embed = i
            
            if interaction.guild_id == server_id:
                templates.append({'server_id': server_id, 'template_name': template_name, 'embed': pickled_embed})
                options_.append(nextcord.SelectOption(label=template_name))

        item = SelectItem(templates, options_)
        view = nextcord.ui.View()
        view.add_item(item)

        await interaction.send('Choose', view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(EventsCog(bot))
