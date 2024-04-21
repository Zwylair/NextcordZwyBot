import pickle
import nextcord.ext.commands
from events.funcs import *
import db


class CreateEmbedView(nextcord.ui.View):
    def __init__(
            self, bot: nextcord.ext.commands.Bot,
            base_interaction: nextcord.Interaction,
            embed_message: nextcord.PartialInteractionMessage,
            out_embed: nextcord.Embed,
            out_chat: nextcord.TextChannel
    ):
        super().__init__()

        self.bot = bot
        self.base_interaction = base_interaction
        self.embed_message = embed_message
        self.out_embed = out_embed
        self.out_chat = out_chat
        self.give_role: nextcord.Role | None = None

    def que_check(self, message: nextcord.Message):
        return self.base_interaction.user.id == message.author.id

    async def command_sender_check(self, interaction: nextcord.Interaction):
        return self.base_interaction.user.id == interaction.user.id

    async def update_embed(self):
        await self.embed_message.edit(content='Предпоказ сообщения', embed=self.out_embed, view=self)

    async def update_out_embed(
            self, title: str | None = None,
            desc: str | None = None,
            colour: int | None = None,
            banner_url: str | None = None,
            thumb_url: str | None = None
    ):
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
        if not await self.command_sender_check(interaction):
            return

        cur = db.get_cursor()
        cur.execute("SELECT * FROM event_templates WHERE server_id = ?", (interaction.guild_id,))
        rows = cur.fetchall()
        cur.close()

        if len(rows) == 5:
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Для одного сервера можно сохранить не более 5 шаблонов!')
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return

        que = await interaction.send('Отправьте название шаблона в чат (не больше 256 символов)', ephemeral=True)
        name_answer = await self.bot.wait_for('message', check=self.que_check)
        name_answer: nextcord.Message = await name_answer.channel.fetch_message(name_answer.id)

        if len(name_answer.content) > 256:
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Название превышает 256 символов!')
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return

        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute('INSERT INTO event_templates (server_id, template_name, embed_bytes) VALUES (?, ?, ?)',
                    (interaction.guild_id, name_answer.content, pickle.dumps(self.out_embed)))
        conn.commit()
        cur.close()

        await interaction.send('Сохранено', ephemeral=True)
        await name_answer.delete()
        await que.delete()

    @nextcord.ui.button(label='Изменить название')
    async def edit_embed_title(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self.command_sender_check(interaction):
            return

        que = await interaction.send('Отправьте заголовок в чат (не больше 256 символов)', ephemeral=True)
        title_answer = await self.bot.wait_for('message', check=self.que_check)
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
        if not await self.command_sender_check(interaction):
            return

        que = await interaction.send('Отправьте описание в чат (не больше 2048 символов)', ephemeral=True)
        description_answer = await self.bot.wait_for('message', check=self.que_check)
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
        if not await self.command_sender_check(interaction):
            return

        que = await interaction.send('Отправьте ссылку на баннер в чат (gif/jpg/png)', ephemeral=True)
        banner_answer = await self.bot.wait_for('message', check=self.que_check)
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
        if not await self.command_sender_check(interaction):
            return

        que = await interaction.send('Отправьте цвет в формате hex, пример: `#f73a02`', ephemeral=True)
        color_answer = await self.bot.wait_for('message', check=self.que_check)
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
        if not await self.command_sender_check(interaction):
            return

        que = await interaction.send('Отправьте ссылку на баннер в чат (jpg/png)', ephemeral=True)
        banner_answer = await self.bot.wait_for('message', check=self.que_check)
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
