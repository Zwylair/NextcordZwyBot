from typing import Literal
import datetime
import nextcord.ext.commands
import settings
from basic_funcs import check_for_event_creator_role
from metacore.db import EVENT_DICT


class HappyPdor(nextcord.ext.commands.Cog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name='events', description='Создать событие',
                            guild_ids=[settings.HAPPY_SQUAD_GUILD_ID, settings.TEST_GUILD_ID])
    async def create_eventrtt(self, interaction: nextcord.Interaction,
                           event_embed_type: Literal[
                               'bunker', 'mafia', 'among us', 'minecraft uhc', 'dota 2 role close', 'zxc metacore', 'karaoke', 'cs role close'] = nextcord.SlashOption(
                               name='event_type', description='Событие', required=True),
                           day: Literal[
                               'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] = nextcord.SlashOption(
                               name='day', description='День проведения ивента', required=True),
                           time: str = nextcord.SlashOption(name='time',
                                                            description='Время проведения ивента (например 21:00)',
                                                            required=True),
                           url: str = nextcord.SlashOption(name='url',
                                                           description='Доп. ссылка на то, что должно меняться в евенте',
                                                           required=False)):
        if not await check_for_event_creator_role(interaction):
            return
        
        input_day_num = {v: k for k, v in settings.DATETIME_WEEKDAY_DICT.items()}[day]
        today_num = datetime.date.today().weekday()
        
        # Ебать сложные махинации с датой я сделал нахуй, я рот ебал нахуй этой хуйни блядота ёбаная
        interval = input_day_num - today_num if today_num < input_day_num else 7 - today_num + input_day_num
        interval = 0 if interval == 7 else interval
        hour, minute = [int(i) for i in time.split(':')]
        date_now = datetime.datetime.utcnow()
        date_now = date_now.replace(hour=hour, minute=minute)
        date_now -= datetime.timedelta(hours=2)  # Hot-fix for host
        timestamp = date_now + datetime.timedelta(days=interval)
        
        embed: nextcord.Embed = EVENT_DICT[event_embed_type]
        embed.timestamp = timestamp
        
        if EVENT_DICT['cs role close'] == embed:
            if url is None:
                await interaction.send('Отсутствует ссылка на регистрацию в турике!', ephemeral=True)
                return
            
            desc = embed.description.split('\n')
            desc[-1] = f'⠀⠀⠀⠀⠀⠀⠀⠀⠀[Ссылка на регистрацию на турнир]({url})'
            embed.description = desc

        if interaction.guild_id == settings.HAPPY_SQUAD_GUILD_ID:
            channel_id = settings.HAPPY_SQUAD_EVENT_CHANNEL_ID
        else:
            channel_id = settings.METACORE_EVENT_CHANNEL_ID if interaction.guild_id == settings.METACORE_GUILD_ID else settings.TEST_METACORE_EVENT_CHANNEL_ID
        channel = interaction.guild.get_channel(channel_id)
        event_message = await channel.send(embed=embed)
        await interaction.send(f'Готово! [Отправленное сообщение...]({event_message.jump_url})', ephemeral=True)


def setup(bot):
    bot.add_cog(HappyPdor(bot))
