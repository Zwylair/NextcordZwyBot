import nextcord.ext.commands
import moderation.roles


class SmallModeratorCog(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='caps_check', description='Проверяет сообщение на капс')
    async def caps_check(self, interaction: nextcord.Interaction,
                         msg_url: str = nextcord.SlashOption(name='message_url', description='Ссылка на проверяемое сообщение')):
        # msg_url = https://discord.com/channels/{server_id}/{channel_id}/{message_id}
        # ['https:', '', 'discord.com', 'channels', '{server_id}', '{channel_id}', '{message_id}']
        
        match msg_url.split('/'):
            case ['https:', '', 'discord.com', 'channels', _, channel_id, message_id, *_]:
                # Get input message content
                try:
                    channel = self.bot.get_channel(int(channel_id))

                    msg_content = await channel.fetch_message(int(message_id))
                    msg_content = str(msg_content.content)

                    # .islower() doesn't detect the digits or spec symbols, it returns False
                    all_chars_count = len([i for i in msg_content.lower() if i.islower()])
                    uppercase_chars = len([i for i in msg_content if i.isupper()])

                    caps_percent = round((uppercase_chars / all_chars_count * 100) * 100) / 100.0
                    
                    embed = nextcord.Embed(title=':page_facing_up: Процент капса!', colour=0x00ACC1,
                                           description=f'Капса в [этом]({"/".join(msg_url)}) сообщении: {caps_percent}%')
                    await interaction.send(embed=embed)
                except nextcord.NotFound:
                    embed = nextcord.Embed(title='Ошибка! :stop_sign:', colour=0xEC0D6D,
                                           description='Неверная ссылка на сообщение / Данное сообщение не найдено!')
                    await interaction.send(embed=embed)
                
                except nextcord.Forbidden:
                    embed = nextcord.Embed(title='Ошибка! :stop_sign:', colour=0xEC0D6D,
                                           description='Недостаточно прав для просмотра данного сообщения!')
                    await interaction.send(embed=embed)
            case _:
                embed = nextcord.Embed(title='Ошибка! :stop_sign:', colour=0xEC0D6D,
                                       description='Неверная ссылка на сообщение / Данное сообщение не найдено!')
                await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(moderation.roles.RolesModerationCog(bot))
    bot.add_cog(SmallModeratorCog(bot))
