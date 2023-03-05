from urllib.parse import urlparse
import nextcord
from nextcord.ext.commands import Bot

from verifier.errors import ErrorOrganizer


def check_verifier_args(bot: Bot, chat: nextcord.TextChannel | None = None,
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
        result = urlparse(banner_url)
        errors_organizer.banner_state = not all([result.scheme, result.netloc])
    
    return errors_organizer


async def verifier_error_handler(interaction: nextcord.Interaction, error_org: ErrorOrganizer):
    embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲',
                           description='Возникла ошибка при создании верификатора! Ошибки:')
    
    if error_org.chat_state:
        embed.add_field(name='Чат 💬', value='Недостаточно прав для просмотра/отправки сообщений в чат!')
    if error_org.colour_state:
        embed.add_field(name='Цвет 🎨', value='Неверно указан цвет! Используйте шаблон: (#rrggbb)')
    if error_org.banner_state:
        embed.add_field(name='Баннер 🚩',
                        value='Неверная ссылка на баннер! Проверьте целостность ссылки и попробуйте ещё раз!')
    
    if error_org.is_one_an_error():
        await interaction.send(embed=embed, ephemeral=True)


class VerifierBaseEmbedView(nextcord.ui.View):
    def __init__(self, bot: nextcord.ext.commands.Bot, base_interaction: nextcord.Interaction,
                 embed_message: nextcord.PartialInteractionMessage, out_embed: nextcord.Embed,
                 out_chat: nextcord.TextChannel):
        super(VerifierBaseEmbedView, self).__init__(timeout=None)
        
        self.bot = bot
        self.base_interaction = base_interaction
        self.embed_message = embed_message
        self.out_embed = out_embed
        self.out_chat = out_chat
        self.give_role: nextcord.Role | None = None
        
        self.out_embed.add_field(name='`(Эта часть сообщения не попадет в финальный вариант сообщения)` ⬇️',
                                 value='Выдаваемая роль:')

    def check(self, message: nextcord.Message):
        return self.base_interaction.user.id == message.author.id
    
    async def check_for_command_sender(self, interaction: nextcord.Interaction):
        return self.base_interaction.user.id == interaction.user.id
    
    async def update_embed(self):
        await self.embed_message.edit(content='Предпоказ сообщения', embed=self.out_embed, view=self)
        
    async def update_out_embed(self, title: str | None = None, desc: str | None = None, colour: int | None = None,
                               banner_url: str | None = None, field_title: str | None = None, field_text: str | None = None):
        title = self.out_embed.title if title is None else title
        desc = self.out_embed.description if desc is None else desc
        colour = self.out_embed.colour if colour is None else colour
        banner_url = self.out_embed.image.url if banner_url is None else banner_url
        field_title = self.out_embed.fields[0].name if field_title is None else field_title
        field_text = self.out_embed.fields[0].value if field_text is None else field_text

        embed = nextcord.Embed(title=title, description=desc, colour=colour)
        embed.set_image(banner_url)
        embed.add_field(name=field_title, value=field_text)

        self.out_embed = embed

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

    @nextcord.ui.button(label='Изменить выдаваемую роль')
    async def edit_embed_role(self, _: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self.check_for_command_sender(interaction):
            return

        que = await interaction.send('Упомяните роль, которую нужно выдавать', ephemeral=True)
        user_answer: nextcord.Message = await self.bot.wait_for("message", check=self.check)

        bot_role = [i for i in interaction.guild.get_member(self.bot.user.id).roles if i.is_bot_managed()][0]
        if not user_answer.role_mentions:
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Не найдена указанная роль!')
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return
        if user_answer.role_mentions[0].position > bot_role.position:
            embed = nextcord.Embed(colour=0xEA5D62, title='Ошибка! 🪲', description='Указанная роль выше чем роль бота!')
            await self.base_interaction.send(embed=embed, ephemeral=True)
            return
        
        self.give_role = user_answer.role_mentions[0]

        await self.update_out_embed(field_title='`(Эта часть сообщения не попадет в финальный вариант сообщения) ⬇️`',
                                    field_text=f'Выдаваемая роль: {self.give_role.mention}')

        await que.delete()
        await user_answer.delete()
        await self.update_embed()
