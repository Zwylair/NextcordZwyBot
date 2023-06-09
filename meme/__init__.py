import os
import nextcord.ext.commands
import PIL.Image
import demapi


class CancelView(nextcord.ui.View):
    def __init__(self, message: nextcord.Message):
        self.message = message
        super().__init__()

    @nextcord.ui.button(label='Отмена', style=nextcord.ButtonStyle.gray)
    async def cancel(self, _: nextcord.ui.Button, __: nextcord.Interaction):
        await self.message.delete()


class MemesCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot
        self.author: nextcord.User | nextcord.Member | None = None
        self.wait_msg: nextcord.Message | None = None
        self.close = False

    def check(self, message: nextcord.Message):
        return self.author.id == message.author.id

    @nextcord.slash_command(name='meme', description='meme')
    async def meme(self, _: nextcord.Interaction):
        pass

    @meme.subcommand(name='demotivator', description='Создать демотиватор')
    async def demotivator(self, interaction: nextcord.Interaction):
        self.author = interaction.user

        attachment: None | nextcord.Attachment = None
        dem_text: None | str = None
        while attachment is None:
            msg = await interaction.send('Отправьте сообщение с картинкой и текстом', ephemeral=True)
            view = CancelView(msg)

            await msg.edit(view=view)
            self.wait_msg = msg
            input_img_msg = await self.bot.wait_for('message', check=self.check)

            try:
                input_img_msg: nextcord.Message = await input_img_msg.channel.fetch_message(input_img_msg.id)
            except BaseException:
                return  # closed

            if input_img_msg.attachments:
                if input_img_msg.content != '':
                    attachment = input_img_msg.attachments[0]
                    dem_text = input_img_msg.content

            await msg.delete()
            await input_img_msg.delete()

        await attachment.save(f'{attachment.filename}-{attachment.id}')

        conf = demapi.Configure(
            base_photo=f'{attachment.filename}-{attachment.id}',
            title=dem_text,
            explanation='',
        )
        image = await conf.coroutine_download()
        image.save(f'{attachment.filename}-{attachment.id}.png')

        await interaction.send(file=nextcord.File(f'{attachment.filename}-{attachment.id}.png'), ephemeral=True)
        os.remove(f'{attachment.filename}-{attachment.id}.png')
        os.remove(f'{attachment.filename}-{attachment.id}')

    @meme.subcommand(name='shakalizator', description='Создать shakalizator')
    async def shakalizator(self, interaction: nextcord.Interaction):
        self.author = interaction.user
    
        attachment: None | nextcord.Attachment = None
        while attachment is None:
            msg = await interaction.send('Отправьте картинку', ephemeral=True)
            view = CancelView(msg)
        
            await msg.edit(view=view)
            self.wait_msg = msg
            input_img_msg = await self.bot.wait_for('message', check=self.check)
        
            try:
                input_img_msg: nextcord.Message = await input_img_msg.channel.fetch_message(input_img_msg.id)
            except BaseException:
                return  # closed
        
            if input_img_msg.attachments:
                attachment = input_img_msg.attachments[0]
        
            await msg.delete()
            await input_img_msg.delete()
    
        await attachment.save(f'{attachment.filename}-{attachment.id}.png')
        img = PIL.Image.open(f'{attachment.filename}-{attachment.id}.png')
        img = img.convert(mode='RGB')

        match img.size:
            case img.size if img.size[0] > 700 or img.size[1] > 700:
                new_size = (int(img.size[0] / 2), int(img.size[1] / 2))
            case img.size if img.size[0] > 1500 or img.size[1] > 1500:
                new_size = (int(img.size[0] / 4), int(img.size[1] / 4))
            case _:
                new_size = img.size

        img = img.resize(new_size)
        img.save(f'{attachment.filename}-{attachment.id}.jpg', quality=8)

        await interaction.send(file=nextcord.File(f'{attachment.filename}-{attachment.id}.jpg'), ephemeral=True)
        os.remove(f'{attachment.filename}-{attachment.id}.png')
        os.remove(f'{attachment.filename}-{attachment.id}.jpg')


def setup(bot):
    bot.add_cog(MemesCog(bot))
